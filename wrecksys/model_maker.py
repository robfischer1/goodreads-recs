import logging
import math
import os
import pathlib
import tarfile
from typing_extensions import Self

from wrecksys.config import ConfigFile
from wrecksys.data.sources import GoodreadsData
from wrecksys.model import callbacks, losses, models, pipeline
from wrecksys.utils import import_tensorflow
tf, keras = import_tensorflow()

logger = logging.getLogger(__name__)

CONFIG_FILE = ConfigFile()
ENV_DATA = 'WRECKSYS_DATA'
ENV_ROOT = 'WRECKSYS_DIR'


class FunctionalModel(object):

    def __init__(self, model_name: str, data_directory=None):
        if not data_directory:
            if ENV_DATA not in os.environ:
                raise ValueError("Please provide a data directory.")
            data_directory = os.getenv(ENV_DATA)

        if ENV_ROOT not in os.environ:
            project_root = pathlib.Path(__file__).parents[1]
        project_root = pathlib.Path(os.getenv(ENV_ROOT))

        self.name = model_name
        self.model: keras.Model = None
        self.config = CONFIG_FILE.data

        self.data = GoodreadsData(data_directory)
        self.dataset = self.data.dataset

        self.root_dir = project_root
        self.directory = pathlib.Path(data_directory) / f'models/{model_name}'
        self.directory.mkdir(parents=True, exist_ok=True)

        self.file = pathlib.Path(self.directory / f"{model_name}.keras")
        self.export_dir = self.directory / 'saved_model'
        self.build_file = self.root_dir / 'build.tar.gz'

        logger.debug("Model wrapper initialized")

    @property
    def _model_config(self):
        return {
            'vocab_size': self.config.vocab_size,
            'embedding_dimensions': self.config.embedding_dimensions,
            'rnn_dimensions': self.config.rnn_dimensions,
            'num_predictions': self.config.num_predictions
        }


    def new(self) -> Self:
        self.model = models.WreckSys(self._model_config, name=self.name)
        return self._compile()

    def load(self) -> Self:
        if self.file.exists():
            self.model = keras.models.load_model(self.file, compile=True)
            return self
        logger.info(f"{self.name} not found, creating new model.")
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
        train, test, val = pipeline.create_training_data(self.data.dataset,
                                                         self.config.num_records,
                                                         self.config.batch_size,
                                                         test_percent=0.1)
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

        export_archive.write_out(str(self.export_dir))
        return self

    def export_to_tflite(self) -> Self:
        tflite_file = str(self.directory / f'{self.name}.tflite')
        converter = tf.lite.TFLiteConverter.from_saved_model(str(self.export_dir))
        tflite_model = converter.convert()
        with tf.io.gfile.GFile(tflite_file, 'wb') as f:
            f.write(tflite_model)
        return self

    def deploy(self) -> Self:
        if not self.directory.exists():
            return self.export_as_saved_model().deploy()

        logger.info(f"Saving project to {self.build_file}")

        app_dir = (self.root_dir / 'webapp/').resolve()
        db_file = self.data.files['database']

        with tarfile.open(self.build_file, 'w:gz') as tar:
            for file in app_dir.rglob('*'):
                tar.add(file, file.relative_to(app_dir.parent))
            for file in self.directory.rglob('*'):
                tar.add(file, pathlib.Path('webapp/assets' / file.relative_to(self.directory)))
            tar.add(db_file, 'webapp/assets/app.db')
        return self


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    test_model = (
        FunctionalModel('rex_test', '/home/rob/projects/wrecksys/data/')
        .load()
        .train_and_eval(rounds=1, epochs=10, limit=100)
        .save()
        .export_as_saved_model()
        .deploy()
    )
