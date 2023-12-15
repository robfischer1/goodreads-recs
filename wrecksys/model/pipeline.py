import logging
import os

from wrecksys.data.datasets import WrecksysDataset
from wrecksys.utils import import_tensorflow
tf, keras = import_tensorflow()

logger = logging.getLogger(__name__)

def sample_record(dataset: tf.data.Dataset) -> dict:
    sample = next(iter(dataset))
    return {k: v[0] for k, v in sample.items()}

def create_training_data(
        data: WrecksysDataset,
        data_size: int,
        batch_size: int,
        test_percent: float) -> tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]:

    d = data.load()
    d = d.apply(tf.data.experimental.assert_cardinality(data_size))

    test_size = int(data_size * test_percent)
    test = d.take(test_size).batch(batch_size=batch_size, drop_remainder=True)
    val = d.skip(test_size).take(test_size).batch(batch_size=batch_size, drop_remainder=True)
    train = d.skip(2*test_size)
    train = train.shuffle(buffer_size=train.cardinality()).batch(batch_size=batch_size, drop_remainder=True)
    logger.debug("Training dataset shuffled")

    return train, test, val

