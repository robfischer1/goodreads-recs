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
from fsspec.callbacks import TqdmCallback
from tqdm.auto import tqdm

from wrecksys import utils
from wrecksys.data import parse

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
        return pd.read_feather(self._output_file, columns=cols, dtype_backend='pyarrow')

    def download(self) -> None:
        if self._output_file.exists():
            self._class_logger.debug(f" {self._output_file} already downloaded.")
            return

        print(f"Fetching {self._url}")
        fs = fsspec.filesystem('http', client_kwargs={'read_timeout': 1200.})
        file_size = fs.info(self._url)['size']

        self._output_file.parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = f"{self._file}.json.gz"
            file = pathlib.Path(temp_dir) / temp_file
            free_space = shutil.disk_usage(file.parent)[2]

            if free_space < 3 * file_size:
                available = utils.display_size(free_space)
                required = utils.display_size(3 * file_size)
                raise OSError(f"Not enough disk space available. Processing {file.name} requires {required} "
                              f"but only {available} is free.")
            else:
                print(f"Disk space OK: {utils.display_size(free_space)} available.")

            fs.get_file(self._url,
                        file,
                        callback=TqdmCallback(
                            tqdm_kwargs={'desc': "Downloading: ", 'file': sys.stdout, 'unit': 'B', 'unit_scale': True}))

            with gzip.open(file) as fp_in:
                gz_size = fp_in.seek(0, io.SEEK_END)
                fp_in.seek(0)
                parse.json_to_feather(fp_in, gz_size, self._output_file)

            print(f"Successfully created {self._output_file}\n")

    def delete(self) -> None:
        if self._example_file.exists():
            pathlib.Path.unlink(self._example_file)
        if self._output_file.exists():
            pathlib.Path.unlink(self._output_file)
