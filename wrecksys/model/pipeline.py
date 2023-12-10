import logging
import os
import pathlib

import numpy as np

from wrecksys.utils import import_tensorflow
tf, keras = import_tensorflow()

logger = logging.getLogger(__name__)


def load_datasets(file: str | os.PathLike, batch_size: int, test_percent: float):
    with open(file, 'rb') as f:
        npz = np.load(f)
        logger.debug(f"Loaded {pathlib.Path(file).name}")
    d = tf.data.Dataset.from_tensor_slices(dict(npz)).cache()
    logger.info("Full tf.data.Dataset created")

    test_size = int(len(d) * test_percent)

    test = d.take(test_size).batch(batch_size=batch_size, drop_remainder=True)
    val = d.skip(test_size).take(test_size).batch(batch_size=batch_size, drop_remainder=True)
    train = d.skip(2*test_size)
    train = train.shuffle(buffer_size=train.cardinality()).batch(batch_size=batch_size, drop_remainder=True)
    logger.debug("Training dataset shuffled")

    return train, test, val

def batch_dataset(ds: tf.data.Dataset, batch: int, desc: str) -> tf.data.Dataset:
    ds = ds.cache().shuffle(buffer_size=ds.cardinality())
    ds = ds.batch(batch_size=batch, drop_remainder=True).prefetch(buffer_size=tf.data.AUTOTUNE)
    logger.info(f"Shuffled and batched {desc} dataset.")
    return ds