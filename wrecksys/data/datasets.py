import logging
import os
import pathlib
import sqlite3

import numpy as np
import pandas as pd

from wrecksys import utils
from wrecksys.config import ConfigFile
from wrecksys.data import download, process

database_filename = 'app.db'
dataset_filename = 'dataset.npz'
ratings_filename = 'clean/ratings.feather'
books_filename = 'clean/books.feather'

logger = logging.getLogger(__name__).parent
config_file = ConfigFile()

ENV_DATA = 'WRECKSYS_DATA'

class GoodreadsData(object):
    def __init__(self, data_directory=None):
        if not data_directory:
            if ENV_DATA not in os.environ:
                raise ValueError("Please provide a data directory.")
            data_directory = os.getenv(ENV_DATA)
        self.config = config_file.data
        self.data_dir = pathlib.Path(data_directory)
        self.data_dir.parent.mkdir(exist_ok=True)

        self.files = self._source_data()
        self.ratings = self.data_dir / ratings_filename
        self.books = self.data_dir / books_filename
        self.database = self.data_dir / database_filename
        self.dataset = self.data_dir / dataset_filename

        self._preload_dataset()

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

    def _source_data(self, dl=False) -> dict[str, download.FileManager]:
        files = utils.source_files(self.config['sources'], self.data_dir)
        return {k: download.FileManager(**v, download=dl) for k, v in files.items()}

    def _preload_dataset(self) -> None:
        if self.database.exists() and self.dataset.exists():
            return
        ratings_df, works_df = self._preload_dataframes()
        self.config.vocab_size = self._build_database(works_df)
        self.config.num_records = self._build_dataset(ratings_df)
        config_file.save()

    def _preload_dataframes(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        if self.ratings.exists() and self.books.exists():
            return pd.read_feather(self.ratings), pd.read_feather(self.books)
        self.files = self._source_data(dl=True)
        ratings_df, works_df = process.prepare_data(self.files)
        ratings_df.to_feather(self.ratings)
        works_df.to_feather(self.books)
        return ratings_df, works_df

    def _build_database(self, df) -> int:
        logger.info(f"Exporting {self.database.name}")
        con = sqlite3.connect(self.database)
        df.to_sql('books', con, index=False, if_exists='replace')
        con.close()
        return len(df)

    def _build_dataset(self, df) -> int:
        logger.info(f"Exporting {self.dataset.name}")
        ids, ratings, labels = process.build_records(df, self.min_length, self.max_length)
        np.savez_compressed(self.dataset, context_id=ids, context_rating=ratings, label_id=labels)
        return len(ids)
