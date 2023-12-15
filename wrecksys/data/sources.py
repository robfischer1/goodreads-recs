import logging
import os
import pathlib

import gdown

from wrecksys import utils
from wrecksys.config import ConfigFile
from wrecksys.data import download, datasets, prepare

# logger = logging.getLogger(__name__).parent
logger = logging.getLogger(__name__)
config_file = ConfigFile()

ENV_DATA = 'WRECKSYS_DATA'
DOWNLOAD = utils.in_notebook()


class GoodreadsData(object):
    def __init__(self, data_directory=None, skip_processing: bool=DOWNLOAD, from_tfrecords=True):
        if not data_directory:
            if ENV_DATA not in os.environ:
                raise ValueError("Please provide a data directory.")
            data_directory = os.getenv(ENV_DATA)

        self.config = config_file.data
        self.cheating = skip_processing
        self.data_dir = pathlib.Path(data_directory)
        self.files = self._get_filepaths()
        self.sources = self._get_source_files()
        self.tfrecords = from_tfrecords
        self.dataset = datasets.TensorflowRecords(**self.dataset_properties)

    @property
    def vocab_size(self) -> int:
        return self.config.vocab_size

    @property
    def num_records(self) -> int:
        return self.config.num_records

    @property
    def min_length(self) -> int:
        return self.config.min_series_length

    @property
    def max_length(self) -> int:
        return self.config.max_series_length

    @property
    def dataset_properties(self) -> dict:
        return {
            'input_file': self.files['ratings'],
            'output_dir': self.files['dataset'],
            'min_length': self.min_length,
            'max_length': self.max_length,
            'num_shards': self.config.num_shards
        }

    def build(self) -> None:
        if self.dataset.exists():
            return

        self._preload_source_data()
        self._preload_dataframes()
        self.config.num_records = self.dataset.build()
        config_file.save()

    def _preload_dataframes(self) -> None:
        if self.files['ratings'].exists() and self.files['works'].exists():
            return
        self.config.vocab_size = prepare.generate_dataframes(self.sources, self.files)


    def _preload_source_data(self):
        if self.cheating and not all([file.exists for file in self.sources.values()]):
            _ = gdown.download_folder(
                id=self.config.remote_storage,
                output=str(self.data_dir / 'raw'),
                quiet=False,
                use_cookies=False)
        for s in self.sources.values():
            s.download()

    def _get_filepaths(self) -> dict[str, pathlib.Path]:
        paths = {
            'database': (self.data_dir / 'app.db').resolve(),
            'dataset': (self.data_dir / 'training').resolve(),
            'ratings': (self.data_dir / 'clean/ratings.feather').resolve(),
            'works': (self.data_dir / 'clean/works.feather').resolve()
        }
        for f in paths.values():
            f.parent.mkdir(parents=True, exist_ok=True)
        paths['dataset'].mkdir(parents=True, exist_ok=True)
        return paths

    def _get_source_files(self) -> dict[str, download.FileManager]:
        sources = self.config['sources']
        data_dir = self.data_dir
        def _parse_url(url: str) -> dict[str, str | pathlib.Path]:
            file_name = utils.get_file_name(url)
            return {
                'url': url,
                'file_name': file_name,
                'example_file': (data_dir / f'examples/{file_name}_example.json').resolve(),
                "output_file": (data_dir / f'raw/{file_name}.feather').resolve()
            }

        file_data = {label: _parse_url(url) for label, url in sources.items()}
        return {k: download.FileManager(**v) for k, v in file_data.items()}


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    test_data = GoodreadsData('/home/rob/projects/wrecksys/data', from_tfrecords=False)
    test_data.build()
