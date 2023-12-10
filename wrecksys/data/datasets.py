import logging
import multiprocessing
import multiprocessing.connection
import os
import pathlib
import sqlite3

import gdown
import numpy as np
import pandas as pd

from wrecksys import utils
from wrecksys.config import ConfigFile
from wrecksys.data import download, process

database_filename = 'app.db'
dataset_filename = 'dataset.npz'
ratings_filename = 'clean/ratings.feather'
books_filename = 'clean/books.feather'

# logger = logging.getLogger(__name__).parent
logger = logging.getLogger(__name__)
config_file = ConfigFile()

ENV_DATA = 'WRECKSYS_DATA'
DOWNLOAD = utils.in_notebook()

class GoodreadsData(object):
    def __init__(self, data_directory=None, skip_processing: bool=DOWNLOAD):
        if not data_directory:
            if ENV_DATA not in os.environ:
                raise ValueError("Please provide a data directory.")
            data_directory = os.getenv(ENV_DATA)
        self.config = config_file.data
        self.data_dir = pathlib.Path(data_directory)
        self.data_dir.parent.mkdir(exist_ok=True)
        self.cheating = skip_processing

        self.files = self._source_data()
        self.ratings = self.data_dir / ratings_filename
        self.books = self.data_dir / books_filename
        self.books.parent.mkdir(exist_ok=True)
        self.database = self.data_dir / database_filename
        self.dataset = self.data_dir / dataset_filename

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

    def preload_dataset(self) -> None:
        if self.database.exists() and self.dataset.exists():
            return
        ratings_df, works_df = self._preload_dataframes()
        self.config.vocab_size = self._build_database(works_df)
        self.config.num_records = self._build_dataset(ratings_df)
        del ratings_df, works_df
        config_file.save()

    def _preload_dataframes(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        if self.ratings.exists() and self.books.exists():
            return pd.read_feather(self.ratings), pd.read_feather(self.books)

        if self.cheating and not all([file.exists for file in self.files.values()]):
            file_list = gdown.download_folder(
                id=self.config.remote_storage,
                output=str(self.data_dir / 'raw'),
                quiet=False,
                use_cookies=False)
            for file in file_list:
                logger.info(f"Successfully downloaded {file} from remote.")
            if len(file_list) < len(self.config.sources):
                self.files = self._source_data(dl=True)
        else:
            self.files = self._source_data(dl=True)

        ratings_df, works_df = process.prepare_data(self.files)
        ratings_df.to_feather(self.ratings)
        works_df.to_feather(self.books)
        return ratings_df, works_df

    def _build_database(self, df: pd.DataFrame) -> int:
        logger.info(f"Exporting {self.database.name}")
        con = sqlite3.connect(self.database)
        df.to_sql('books', con, index=False, if_exists='replace')
        con.close()
        return len(df)

    def _build_dataset(self, df: pd.DataFrame) -> int:
        logger.info(f"Exporting {self.dataset.name}")
        recv_end, send_end = multiprocessing.Pipe(False)
        p = multiprocessing.Process(target=_build_dataset_worker,
                                    args=(df, self.min_length, self.max_length, self.dataset, send_end))
        p.start()
        p.join()
        return recv_end.recv()
#Foo
def _build_dataset_worker(
        df: pd.DataFrame,
        min_len: int,
        max_len: int,
        out_file: pathlib.Path,
        out_pipe: multiprocessing.connection.Connection) -> None:

    ids, ratings, labels = process.build_records(df, min_len, max_len)
    n_records = len(ids)
    with open(out_file, 'wb') as f:
        np.savez_compressed(f, context_id=ids, context_rating=ratings, label_id=labels)
    del ids, ratings, labels
    out_pipe.send(n_records)