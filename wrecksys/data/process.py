import logging
import multiprocessing
import multiprocessing.connection
import os
import pathlib
import sys
from collections import namedtuple

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from wrecksys.utils import import_tensorflow
tf, keras = import_tensorflow()
logger = logging.getLogger(__name__)

UserHistory = namedtuple("UserHistory", "history books ratings")
UserContext = namedtuple("UserContext", "ids ratings label")

RECORD_COUNT = 'WRECKSYS_ROWS'

class SequentialDataset(object):
    _class_logger = logging.getLogger(__name__).getChild(__qualname__)
    def __init__(self,
                 input_file: str | os.PathLike,
                 output_file: str | os.PathLike,
                 min_length: int,
                 max_length: int):

        self.input_file = pathlib.Path(input_file)
        self.output_file = pathlib.Path(output_file)
        self.min_length = min_length
        self.max_length = max_length
        self.size = -1
        self._class_logger.debug(f"Input file: {self.input_file}")
        self._class_logger.debug(f"Output file: {self.output_file}")

    def build(self):
        raise NotImplementedError()

    def delete(self) -> None:
        self.output_file.unlink(missing_ok=True)
        self._class_logger.info(f"Deleted {self.output_file}.")

    def load(self):
        raise NotImplementedError()


    def _from_source(self):
        context_ids = []
        context_ratings = []
        label_ids = []

        df = pd.read_feather(self.input_file, dtype_backend='pyarrow')

        with tqdm(total=len(df.user_id.unique()),
                  desc="Building timelines ",
                  file=sys.stdout,
                  unit=' users') as timeline_progress:
            for _, group in df.groupby('user_id', observed=True):
                books: list = group['work_id'].tolist()
                ratings: list = group['rating'].tolist()

                if len(books) >= self.min_length:
                    user_context_ids, user_context_ratings, user_label_ids = self._build_user_context(books, ratings)
                    context_ids.extend(user_context_ids)
                    context_ratings.extend(user_context_ratings)
                    label_ids.extend(user_label_ids)
                timeline_progress.update(1)
                sys.stdout.flush()

        del df
        n_rows = len(label_ids)
        self._class_logger.info(f"Successfully created {n_rows} training examples.")
        return context_ids, context_ratings, label_ids

    def _build_user_context(
            self,
            books: list[int],
            ratings: list[int]) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray]]:

        user_context_ids = []
        user_context_ratings = []
        user_label_ids = []

        for label in range(1, len(books)):
            pos = max(0, label - self.max_length)
            if (label - pos) >= self.min_length:
                context_id = np.array(books[pos:label], dtype=np.int32)
                context_id.resize(self.max_length)
                context_rating = np.array(ratings[pos:label], dtype=np.float32)
                context_rating.resize(self.max_length)
                label_id = np.array([books[label]], dtype=np.int32)

                user_context_ids.append(context_id)
                user_context_ratings.append(context_rating)
                user_label_ids.append(label_id)

        return user_context_ids, user_context_ratings, user_label_ids

class FeatherDataset(SequentialDataset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build(self) -> None:
        context_ids, context_ratings, label_ids = self._from_source()
        self.size = len(label_ids)
        df = pd.DataFrame.from_dict({'context_id': context_ids,
                                       'context_rating': context_ratings,
                                       'label_id': label_ids})
        del context_ids, context_ratings, label_ids
        df.to_feather(self.output_file)
        self._class_logger.info(f"Saved {self.output_file.name} in {self.output_file.parent}")

    def load(self) -> tf.data.Dataset:
        df = pd.read_feather(self.output_file)
        self._class_logger.info(f"Loaded {self.output_file.name} from {self.output_file.parent}")
        data = {col: df[col].to_list() for col in df}
        del df

        d = tf.data.Dataset.from_tensor_slices((data, data['label_id']))
        return d

class NumpyDataset(SequentialDataset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build(self):
        context_ids, context_ratings, label_ids = self._from_source()
        self.size = len(label_ids)
        with open(self.output_file, 'wb') as f:
            np.savez_compressed(f,
                                context_id=np.array(context_ids),
                                context_rating=np.array(context_ratings),
                                label_id=np.array(label_ids)
                                )

    def load(self):
        with open(self.output_file, 'rb') as f:
            npz = np.load(f)
            labels = npz['label_id']
            logger.debug(f"Loaded {self.output_file.name}")
            return tf.data.Dataset.from_tensor_slices((dict(npz), labels))


class TFRecordsDataset(SequentialDataset):
    def __init__(self, num_shards, *args, **kwargs):
        self.num_shards = num_shards
        super().__init__(*args, **kwargs)
        self.output_file = self.output_file.parent
        self.file_template = 'goodreads{:02}.tfrecord'

    def build(self):
        if self.num_shards == len([f for f in self.output_file.glob('*.tfrecord')]):
            return

        records = []
        file_count = 0

        df = pd.read_feather(self.input_file, dtype_backend='pyarrow')
        self.size = len(df)
        cutoff = self.size // self.num_shards

        with tqdm(total=len(df.user_id.unique()),
                  desc="Building timelines ",
                  file=sys.stdout,
                  unit=' users') as timeline_progress:
            for _, group in df.groupby('user_id', observed=True):
                books: list = group['work_id'].tolist()
                ratings: list = group['rating'].tolist()

                if len(books) >= self.min_length:
                    user_examples = self._build_user_context(books, ratings)
                    records.extend(user_examples)

                if len(records) >= cutoff:
                    _write_tf_records(records,
                                      str(self.output_file /
                                          self.file_template.format(file_count)))
                    file_count += 1
                    records = []

                timeline_progress.update(1)
                sys.stdout.flush()

            if records:
                _write_tf_records(records,
                                  str(self.output_file /
                                      self.file_template.format(file_count)))
                file_count += 1
                del df, records

        self._class_logger.info(f"Successfully created {self.size} training examples in {file_count} files.")

    def _build_user_context(self, books: list[int], ratings: list[int]) -> list[tf.train.Example]:

        examples = []

        for label in range(1, len(books)):
            pos = max(0, label - self.max_length)
            if (label - pos) >= self.min_length:
                context_id = np.array(books[pos:label], dtype=np.int32)
                context_id.resize(self.max_length)
                context_rating = np.array(ratings[pos:label], dtype=np.float32)
                context_rating.resize(self.max_length)
                label_id = np.array([books[label]], dtype=np.int32)

                example = _create_tf_example(context_id, context_rating, label_id)
                examples.append(example)

        return examples



def create_training_data(source_file: pathlib.Path,
                         destination: str,
                         min_length: int,
                         max_length: int,
                         num_shards: int | None=None,
                         tf_records=False) -> int:

    os.environ[RECORD_COUNT] = '0'
    p = multiprocessing.Process(target=_create_training_data_worker,
                                args=(
                                    str(source_file),
                                    destination,
                                    min_length,
                                    max_length,
                                    num_shards,
                                    tf_records
                                ))
    dataset_type = 'TFRecords' if tf_records else 'Numpy'
    logger.info(f"Creating {dataset_type} dataset.")
    p.start()
    p.join()
    return int(os.environ.pop(RECORD_COUNT))


def _create_training_data_worker(source: str,
                                 destination: str,
                                 min_length: int,
                                 max_length: int,
                                 num_shards: int | None = None,
                                 tf_records=False) -> None:

    save_fn: callable = _contexts_to_examples if tf_records else _contexts_to_numpy
    logger.debug(f"Loading {source}")
    df = pd.read_feather(source, dtype_backend='pyarrow')
    timelines = build_timelines(df)
    contexts = build_contexts(timelines, min_length, max_length)
    os.environ[RECORD_COUNT] = str(len(contexts))
    save_fn(contexts, destination, num_shards)


def _contexts_to_examples(contexts: list[UserContext], output_file: str, num_shards: int) -> None:
    dataset_dir = pathlib.Path(output_file).parent.resolve()
    logger.debug("Generating examples")
    examples = [_create_tf_example(context.ids, context.ratings, context.label) for context in contexts]
    logger.debug("Examples generated")
    shards = np.array_split(examples, num_shards)
    for i in range(num_shards):
        logger.debug(f"Writing file {i}")
        logger.debug(f"{shards[i][0]}")
        _write_tf_records(shards[i], str(dataset_dir / RECORD_TEMPLATE.format(i)))


def _create_tf_example(context_id, context_rating, label_id):
    return tf.train.Example(
        features=tf.train.Features(
            feature={
                "context_id": tf.train.Feature(int64_list=tf.train.Int64List(value=context_id)),
                "context_rating": tf.train.Feature(float_list=tf.train.FloatList(value=context_rating)),
                "label_id": tf.train.Feature(int64_list=tf.train.Int64List(value=label_id))
            }
        )
    )


def _write_tf_records(tf_examples, filename):
    logger.debug(f"Writing {len(tf_examples):,} records to {filename}")
    with tf.io.TFRecordWriter(filename) as f:
        for example in tf_examples:
            f.write(example.SerializeToString())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.debug("Huh?")


    test_ds = TFRecordsDataset(input_file='../../data/clean/ratings.feather',
                               output_file='../../data/dataset/file.format',
                               min_length=3,
                               max_length=10,
                               num_shards=10)

    test_ds.build()