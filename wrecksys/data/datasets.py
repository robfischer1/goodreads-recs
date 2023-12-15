import abc
import logging
import os
import pathlib
import sys
import typing

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from wrecksys.utils import import_tensorflow
tf, keras = import_tensorflow()
logger = logging.getLogger(__name__)


def sample_record(dataset: tf.data.Dataset):
    sample = next(iter(dataset))
    return {k: v[0] for k, v in sample.items()}


class SingleExample(typing.NamedTuple):
    ids: list[int]
    ratings: list[int]
    label: list[int]

class WrecksysDataset(abc.ABC):
    @abc.abstractmethod
    def build(self) -> None:
        pass

    @abc.abstractmethod
    def exists(self) -> bool:
        pass

    @abc.abstractmethod
    def delete(self) -> None:
        pass

    @abc.abstractmethod
    def load(self) -> tf.data.Dataset:
        pass

class TensorflowRecords(WrecksysDataset):
    _class_logger = logging.getLogger(__name__).getChild(__qualname__)
    def __init__(self,
                 input_file: str | os.PathLike,
                 output_dir: str | os.PathLike,
                 file_names: str = 'goodreads',
                 min_length: int = 3,
                 max_length: int = 10,
                 num_shards: int = 10):

        self.input_file = pathlib.Path(input_file)
        self.output_dir = pathlib.Path(output_dir)
        self.file_template = f'{file_names}{{:02}}.tfrecord'

        self.min_length = min_length
        self.max_length = max_length
        self.num_shards = num_shards
        self.size = -1

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._class_logger.debug(f"Input file: {self.input_file}")
        self._class_logger.debug(f"Output directory: {self.output_dir}")

    def build(self) -> int | None:
        if self.exists():
            self._class_logger.debug("Dataset already built.")
            return

        records = []

        df = pd.read_feather(self.input_file, dtype_backend='pyarrow')

        with tqdm(total=len(df.user_id.unique()),
                  desc="Building user timelines ",
                  file=sys.stdout,
                  unit=' users') as timeline_progress:
            for _, group in df.groupby('user_id', observed=True):
                books: list = group['work_id'].tolist()
                ratings: list = group['rating'].tolist()

                if len(books) >= self.min_length:
                    user_examples = self._build_single_examples(books, ratings)
                    records.extend(user_examples)

                timeline_progress.update(1)

        del df

        self.size = len(records)
        n = self.size // self.num_shards
        chunks = [records[x:x+n] for x in range(0, self.size, n)]
        for i in range(self.num_shards):
            self._write_tf_records(chunks[i], i)

        self._class_logger.info(f"Successfully created {self.size} training examples in {len(chunks)} files.")
        return self.size

    def delete(self) -> None:
        for file in self.output_dir.iterdir():
            file.unlink()
        self.output_dir.rmdir()
        self._class_logger.info(f"Removed {self.output_dir}.")

    def exists(self) -> bool:
        return self.num_shards == len([f for f in self.output_dir.glob('*.tfrecord')])

    def load(self) -> tf.data.Dataset:
        if not self.exists():
            self.build()

        # Sadly, TensorFlow doesn't like Path objects.
        files = [str(f) for f in self.output_dir.glob('*.tfrecord')]
        feature_description = {
            'context_id': tf.io.FixedLenFeature(
                [self.max_length], tf.int64, default_value=np.repeat(0, self.max_length)),
            'context_rating': tf.io.FixedLenFeature(
                [self.max_length], tf.float32, default_value=np.repeat(3, self.max_length)),
            'label_id': tf.io.FixedLenFeature([1], tf.int64)
        }

        def _parse(example):
            features = tf.io.parse_single_example(example, feature_description)
            features['context_id'] = tf.cast(features['context_id'], tf.int32)
            features['label_id'] = tf.cast(features['label_id'], tf.int32)
            return features, features['label_id']

        d = tf.data.TFRecordDataset(files)
        d = d.map(_parse, num_parallel_calls=tf.data.AUTOTUNE)
        d = d.cache()
        return d

    def _build_single_examples(self, books: list[int], ratings: list[int]) -> list[SingleExample]:
        examples = []

        for label in range(1, len(books)):
            pos = max(0, label - self.max_length)
            length = label - pos

            if length >= self.min_length:
                dif = self.max_length - length
                pad = [0 for _ in range(dif)]

                context_id = books[pos:label] + pad
                context_rating = ratings[pos:label] + pad
                label_id = [books[label]]

                examples.append(SingleExample(context_id, context_rating, label_id))

        return examples


    def _write_tf_records(self, examples, file_num) -> None:

        filename = str(self.output_dir / self.file_template.format(file_num))
        logger.debug(f"Writing {len(examples):,} records to {filename}")
        tf_examples = []

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

        with tqdm(total=len(examples),
                  desc=f"Creating TFRecords ({file_num+1}/{self.num_shards}): ",
                  file=sys.stdout,
                  unit=' examples') as conversion_progress:
            for example in examples:
                tf_examples.append(_create_tf_example(*example))
                conversion_progress.update(1)

        with tf.io.TFRecordWriter(filename) as f:
            for example in tf_examples:
                f.write(example.SerializeToString())



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)