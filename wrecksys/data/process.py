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
from typing_extensions import Self

from wrecksys.utils import import_tensorflow
tf, keras = import_tensorflow()
logger = logging.getLogger(__name__)

UserHistory = namedtuple("UserHistory", "history books ratings")
UserContext = namedtuple("UserContext", "ids ratings label")

RECORD_TEMPLATE = 'goodreads{:02}.tfrecord'
RECORD_COUNT = 'WRECKSYS_ROWS'

class BaseDataset(object):
    def __init__(self,
                 input_file: str | os.PathLike,
                 output_file: str | os.PathLike,
                 min_length: int,
                 max_length: int):

        self.input_file = pathlib.Path(input_file)
        self.output_file = pathlib.Path(output_file)
        self.min_length = min_length
        self.max_length = max_length

        self.data = None

    def clear(self) -> None:
        self.data = None

    def to_feather(self, file: str | os.PathLike) -> None:
        context_ids, context_ratings, label_ids = self.data
        df = pd.DataFrame.from_dict({'context_id': context_ids,
                                       'context_rating': context_ratings,
                                       'label_id': label_ids})
        df.to_feather(pathlib.Path(file))

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

        self.data = context_ids, context_ratings, label_ids

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
                context_id = np.array(books[pos:label], dtype=np.int32).reshape(10)
                context_rating = np.array(ratings[pos:label], dtype=np.float32).reshape(10)
                label_id = np.array([books[label]], dtype=np.int32)

                user_context_ids.append(np.array(context_id, dtype=np.int32))
                user_context_ratings.append(np.array(context_rating, dtype=np.float32))
                user_label_ids.append(np.array(label_id, dtype=np.int32))

        return user_context_ids, user_context_ratings, user_label_ids



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


def _contexts_to_numpy(contexts: list[UserContext], output_file: str, num_shards=None) -> None:
    output_file = pathlib.Path(output_file)
    context_ids = []
    context_ratings = []
    label_ids = []

    for context in contexts:
        context_id = np.array(context.ids, dtype=np.int32)
        context_ids.append(context_id)

        context_rating = np.array(context.ratings, dtype=np.float32)
        context_ratings.append(context_rating)

        label_id = np.array(context.label, dtype=np.int32)
        label_ids.append(label_id)

    with open(output_file, 'wb') as f:
        np.savez_compressed(f,
                            context_id=np.array(context_ids),
                            context_rating=np.array(context_ratings),
                            label_id=np.array(label_ids)
                            )

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
    logger.debug(f"Writing {len(tf_examples)} to {filename}")
    with tf.io.TFRecordWriter(filename) as f:
        for example in tf_examples:
            f.write(example.SerializeToString())


def build_timelines(df: pd.DataFrame) -> list[UserHistory]:
    timelines = []

    with tqdm(total=len(df.user_id.unique()),
              desc="Building timelines ",
              file=sys.stdout,
              unit=' users') as timeline_progress:
        for _, group in df.groupby('user_id', observed=True):
            books: list = group['work_id'].tolist()
            ratings: list = group['rating'].tolist()
            size: int = len(books)
            user_history = UserHistory(size, books, ratings)
            timelines.append(user_history)
            timeline_progress.update(1)

    return timelines


def build_contexts(timeline: list[UserHistory], min_length: int, max_length: int) -> list[UserContext]:
    contexts = []
    with tqdm(total=len(timeline),
              desc="Building contexts ",
              file=sys.stdout,
              unit=' timelines') as conversion_progress:
        for user in timeline:
            if user.history < min_length:
                conversion_progress.update(1)
                continue
            user_contexts = build_user_context(user, min_length, max_length)
            contexts.extend(user_contexts)
            conversion_progress.update(1)
    return contexts



def build_user_context(user: UserHistory, min_length: int, max_length: int) -> list[UserContext]:
    user_contexts = []

    for label in range(1, len(user.books)):
        pos = max(0, label - max_length)
        if (label - pos) >= min_length:
            context_id = user.books[pos:label]
            context_rating = user.ratings[pos:label]
            label_id = [user.books[label]]
            while len(context_id) < max_length:
                context_id.append(0)
                context_rating.append(0)
            user_contexts.append(UserContext(context_id, context_rating, label_id))
    return user_contexts

