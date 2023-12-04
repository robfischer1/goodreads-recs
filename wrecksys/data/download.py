import csv
import gzip
import io
import json
import logging
import pathlib
import shutil
import sys
import tempfile

import fsspec
import pandas as pd
import pyarrow.feather as feather
from fsspec.callbacks import TqdmCallback
from pyarrow import json as pa_json
from tqdm.auto import tqdm

from wrecksys import utils

logger = logging.getLogger(__name__)

class TqdmAutoCallback(TqdmCallback):
    """
    Overrides the constructor for the provided TqdmCallback to use tqdm.auto instead
    """
    def __init__(self, tqdm_kwargs=None, *args, **kwargs):
        self._tqdm = tqdm
        self._tqdm_kwargs = tqdm_kwargs or {}
        super(TqdmCallback, self).__init__(*args, **kwargs)


class FileManager(object):
    _class_logger = logging.getLogger(__name__).getChild(__qualname__)

    def __init__(self, url: str, file_name: str, example_file: pathlib.Path, output_file: pathlib.Path, download=False):
        self._url = url
        self._file = file_name
        self._example_file = example_file
        self._output_file = output_file

        if download:
            self.download()

    @property
    def example(self) -> dict:
        file = self._example_file
        if not file.exists():
            file.parent.mkdir(parents=True, exist_ok=True)
            return self._generate_example()

        with file.open('r') as example:
            return json.load(example)

    def _generate_example(self) -> dict:
        self._class_logger.info(f" Generating new {self._example_file.name}")
        with open(self._example_file, 'w', encoding='utf-8') as example:
            with fsspec.open(self._url, 'rt', compression='infer') as source:
                first_line: dict = json.loads(source.readline())
                json.dump(first_line, example, indent=4)
                return first_line

    def dataframe(self, cols=None) -> pd.DataFrame:
        if not self._output_file.exists():
            self.download()
        self._class_logger.info(f" Reading {self._output_file.name}")
        return pd.read_feather(self._output_file, columns=cols)


    def download(self) -> None:
        if self._output_file.exists():
            self._class_logger.debug(f" {self._output_file} already downloaded.")
            return

        print(f"Fetching {self._url}")
        fs = fsspec.filesystem('http', client_kwargs={'read_timeout': 1200.})
        self._output_file.parent.mkdir(exist_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = pathlib.Path(temp_dir) / f"{self._file}.json.gz"
            csv_file = json_file.with_suffix('').with_suffix('.csv')

            fs.get_file(self._url,
                        json_file,
                        callback=TqdmCallback(
                            tqdm_kwargs={'desc': "Downloading: ", 'file': sys.stdout, 'unit': 'B', 'unit_scale': True}))

            with gzip.open(json_file) as input_file:
                logger.debug(f'Generating {csv_file.name}')
                with open(csv_file, 'w', newline='', encoding='utf_8') as temp_file:
                    writer = csv.writer(temp_file)
                    line = input_file.readline()
                    obj = json.loads(line)
                    columns = obj.keys()
                    writer.writerow(columns)
                    writer.writerow([str(obj[col]) for col in columns])
                    for line in input_file.readlines():
                        obj = json.loads(line)
                        writer.writerow([str(obj[col]) for col in columns])
                logger.debug(f'Creating {self._file} dataframe')
                df = pd.read_csv(csv_file)
                logger.debug(f'Writing {self._output_file}')
                df.to_feather(self._output_file)



            print(f"Successfully created {self._output_file}\n")

    def delete(self) -> None:
        if self._example_file.exists():
            pathlib.Path.unlink(self._example_file)
        if self._output_file.exists():
            pathlib.Path.unlink(self._output_file)
