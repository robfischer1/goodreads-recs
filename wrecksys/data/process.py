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

RECORD_TEMPLATE = 'goodreads{:02}.tfrecord'
RECORD_COUNT = 'WRECKSYS_ROWS'

def create_training_data(source_file: pathlib.Path,
                         destination: str,
                         min_length: int,
                         max_length: int,
                         num_shards: int | None=None,
                         tf_records=False) -> int:
    if tf_records:
        target_dir = pathlib.Path(destination)
        if target_dir.is_file():
            raise NotADirectoryError("Please specify a valid directory for TF_Records.")
        target_dir.mkdir(parents=True, exist_ok=True)

    if not source_file.exists():
        raise FileNotFoundError(f"Could not find {source_file.name} in {source_file.parent}")

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

def _contexts_to_examples(contexts: list[UserContext], dataset_dir: str, num_shards: int) -> None:

    def _create_tf_example(context_id, context_rating, label_id):
        return tf.train.Example(
            features=tf.train.Features(
                feature={
                    "context_id": tf.train.Feature(int64_list=tf.train.Int32List(value=context_id)),
                    "context_rating": tf.train.Feature(float_list=tf.train.FloatList(value=context_rating)),
                    "label_id": tf.train.Feature(int64_list=tf.train.Int32List(value=[label_id]))
                }
            )
        )

    def _write_tf_records(tf_examples, filename):
        with tf.io.TFRecordWriter(filename) as f:
            for example in tf_examples:
                f.write(example.SerializeToString())

    examples = [_create_tf_example(context.ids, context.ratings, context.label) for context in contexts]
    shards = np.array_split(examples, num_shards)
    for i in range(num_shards):
        _write_tf_records(shards[i], dataset_dir + RECORD_TEMPLATE.format(i))


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
