import logging
import math
import os
import pathlib
from typing_extensions import Self

from wrecksys import utils
tf, keras = utils.import_tensorflow()

from wrecksys.config import ConfigFile
from wrecksys.data.datasets import GoodreadsData
from wrecksys.model import callbacks, losses, models, pipeline


logger = logging.getLogger(__name__)
WRECKSYS_DATA = os.environ.get('WRECKSYS_DATA', None)
CONFIG_FILE = ConfigFile()

class FunctionalModel(object):

    def __init__(self, model_name: str, data_directory: str | os.PathLike = WRECKSYS_DATA):
        if data_directory is None:
            raise ValueError("Please provide a data directory.")
        self.name = model_name
        self.data = GoodreadsData(data_directory)
        self.config = CONFIG_FILE.data
        self.directory = pathlib.Path(data_directory) / f"models/{model_name}/"
        self.file = self.directory / f"{model_name}.keras"
        self.file.parent.mkdir(exist_ok=True)
        self.model: keras.Model = None
        logger.debug("Model wrapper initialized")

    def new(self) -> Self:
        self.model = models.WreckSys(dict(self.config), name=self.name)
        return self._compile()

    def load(self) -> Self:
        if self.file.exists():
            self.model = keras.models.load_model(self.file, compile=True)
            return self
        return self.new()

    def _compile(self) -> Self:
        if self.model:
            self.model.compile(
                optimizer=keras.optimizers.experimental.Adagrad(learning_rate=0.065, epsilon=1e-06),
                loss=losses.GlobalSoftmax()
            )
            logger.debug("New model compiled.")
            return self

    def train_and_eval(self, rounds=1, epochs=1, limit=None) -> Self:
        logger.debug("Entering the training loop")
        train, test, val = pipeline.load_datasets(self.data.dataset, self.config.batch_size, 0.1)
        val_steps = math.ceil(len(val) // self.config.batch_size)
        for _ in range(rounds):
            use_callbacks = callbacks.callback_list(self.model, self.directory)
            self.model.fit(train,
                           validation_data=val,
                           validation_steps=val_steps,
                           epochs=epochs,
                           steps_per_epoch=limit,
                           callbacks=use_callbacks,
                           verbose=1)
            self.model.evaluate(test, steps=limit, callbacks=use_callbacks)
        return self

    def save(self) -> Self:
        self.model.save(self.file)
        return self

    def export_as_saved_model(self) -> Self:
        export_dir = str(self.directory / 'saved_model')
        export_archive = keras.export.ExportArchive()
        dummy_input = {
            'context_id': tf.range(10),
            'context_rating': tf.ones(10),
        }

        export_archive.track(self.model)
        self.model.serve(**dummy_input)
        export_archive.add_endpoint(
            name='serve',
            fn=self.model.serve,
        )

        export_archive.write_out(export_dir)
        return self

    def export_to_tflite(self) -> Self:
        tflite_file = str(self.directory / f'{self.name}.tflite')
        export_dir = str(self.directory / 'saved_model')
        converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
        tflite_model = converter.convert()
        with tf.io.gfile.GFile(tflite_file, 'wb') as f:
            f.write(tflite_model)
        return self


if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    logger.setLevel(logging.INFO)

    test_model = (
        FunctionalModel('rex2', '/home/rob/projects/capstone/data/')
        .load()
        .train_and_eval(rounds=10)
        .save()
        .export_as_saved_model()
    )


