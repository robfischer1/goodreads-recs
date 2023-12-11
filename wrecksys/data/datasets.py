import logging
import os
import pathlib
import sqlite3

import gdown
import pandas as pd

from wrecksys import utils
from wrecksys.config import ConfigFile
from wrecksys.data import download, process, prepare

# logger = logging.getLogger(__name__).parent
logger = logging.getLogger(__name__)
config_file = ConfigFile()

ENV_DATA = 'WRECKSYS_DATA'
DOWNLOAD = utils.in_notebook()


def _properties_from_url(url: str, dest_dir: pathlib.Path) -> dict[str, str | pathlib.Path]:
    file_name = utils.get_file_name(url)
    return {
        'url': url,
        'file_name': file_name,
        'example_file': (dest_dir / f'examples/{file_name}_example.json').resolve(),
        "output_file": (dest_dir / f'raw/{file_name}.feather').resolve()
    }


def _properties_from_dir(data_dir: pathlib.Path) -> dict[str, pathlib.Path]:
    paths = {
        'database': data_dir / 'app.db',
        'dataset': data_dir / 'training/numpy_dataset.npz',
        'ratings': data_dir / 'clean/ratings.feather',
        'works': data_dir / 'clean/works.feather'
    }
    for f in paths.values():
        f.parent.mkdir(parents=True, exist_ok=True)
    return paths


def _get_source_files(sources: dict[str, str], data_dir: pathlib.Path) -> dict[str, download.FileManager]:
    file_data = { label: _properties_from_url(url, data_dir) for label, url in sources.items() }
    return {k: download.FileManager(**v) for k, v in file_data.items()}


class GoodreadsData(object):
    def __init__(self, data_directory=None, skip_processing: bool=DOWNLOAD, from_tfrecords=True):
        if not data_directory:
            if ENV_DATA not in os.environ:
                raise ValueError("Please provide a data directory.")
            data_directory = os.getenv(ENV_DATA)


        self.config = config_file.data
        self.cheating = skip_processing
        self.data_dir = pathlib.Path(data_directory)
        self.files = _properties_from_dir(self.data_dir)
        self.sources = _get_source_files(self.config['sources'], self.data_dir)
        self.tfrecords = from_tfrecords

    @property
    def vocab_size(self):
        return self.config.vocab_size

    @property
    def num_records(self):
        return self.config.num_records

    @property
    def min_length(self):
        return self.config.min_series_length

    @property
    def max_length(self):
        return self.config.max_series_length

    def build(self) -> None:
        dataset_dir = self.files['dataset'].parent
        num_shards = self.config.num_shards
        if self.tfrecords:
            if num_shards == len([f for f in dataset_dir.glob('*.tfrecord')]):
                return
        else:
            if self.files['dataset'].exists():
                return

        self._preload_source_data()
        self._preload_dataframes()
        self.config.num_records = process.create_training_data(
            self.files['ratings'],
            str(self.files['dataset']),
            self.min_length,
            self.max_length,
            num_shards,
            self.tfrecords
        )
        config_file.save()

    def _preload_dataset(self) -> None:
        if self.files['database'].exists() and self.files['dataset'].exists():
            return
        self._preload_dataframes()


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