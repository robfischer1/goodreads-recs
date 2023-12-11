import logging
import os
import pathlib

import numpy as np

from wrecksys.utils import import_tensorflow
tf, keras = import_tensorflow()

logger = logging.getLogger(__name__)

def sample_record(dataset: tf.data.Dataset) -> dict:
    sample = next(iter(dataset))
    return {k: v[0] for k, v in sample.items()}

def load_datasets(
        source: str | os.PathLike,
        n_records: int,
        batch_size: int,
        feature_length: int,
        test_percent: float,
        from_tf_records=True) -> tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]:

    if from_tf_records:
        d = _load_tfrecords_dataset(source, feature_length)
    else:
        d = _load_numpy_dataset(source)

    d = d.apply(tf.data.experimental.assert_cardinality(n_records))
    d = d.cache()
    d = d.prefetch(buffer_size=tf.data.AUTOTUNE)
    logger.info("Full tf.data.Dataset created")

    test_size = int(n_records * test_percent)

    test = d.take(test_size).batch(batch_size=batch_size, drop_remainder=True)
    val = d.skip(test_size).take(test_size).batch(batch_size=batch_size, drop_remainder=True)
    train = d.skip(2*test_size)
    train = train.shuffle(buffer_size=train.cardinality()).batch(batch_size=batch_size, drop_remainder=True)
    logger.debug("Training dataset shuffled")

    return train, test, val

def _load_tfrecords_dataset(directory: str | os.PathLike, feature_length: int) -> tf.data.Dataset:
    def _parse(example):
        features = tf.io.parse_single_example(example, {
            'context_id': tf.io.FixedLenFeature([feature_length], tf.int32, default_value=np.repeat(0, feature_length)),
            'context_rating': tf.io.FixedLenFeature([feature_length], tf.float32, default_value=np.repeat(3, feature_length)),
            'label_id': tf.io.FixedLenFeature([1], tf.int32)
        })
        features['context_id'] = tf.cast(features['context_id'], tf.int32)
        features['label_id'] = tf.cast(features['label_id'], tf.int32)
        return features, features['label_id']

    dataset_dir = pathlib.Path(directory).parent
    dataset_files = [str(f) for f in dataset_dir.glob('*.tfrecord')]

    return tf.data.TFRecordDataset(dataset_files).map(_parse, num_parallel_calls=tf.data.AUTOTUNE)

def _load_numpy_dataset(file: str | os.PathLike) -> tf.data.Dataset:
    with open(file, 'rb') as f:
        npz = np.load(f)
        labels = npz['label_id']
        logger.debug(f"Loaded {pathlib.Path(file).name}")
        return tf.data.Dataset.from_tensor_slices((dict(npz), labels))


def _batch_numpy_dataset(ds: tf.data.Dataset, batch: int, desc: str) -> tf.data.Dataset:
    ds = ds.cache().shuffle(buffer_size=ds.cardinality())
    ds = ds.batch(batch_size=batch, drop_remainder=True).prefetch(buffer_size=tf.data.AUTOTUNE)
    logger.info(f"Shuffled and batched {desc} dataset.")
    return ds