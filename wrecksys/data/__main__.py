import argparse
import logging
import os
import pathlib

from wrecksys.data.datasets import GoodreadsData

data_parser = argparse.ArgumentParser(
    prog='wrecksys.data',
    description='Downloads the Goodreads dataset for use in wrecksys.model'
)
d = data_parser.add_argument('-d', '--datadir',
                         help='Working directory for storing data files',
                         dest='data_dir',
                         metavar='data_directory',
                         type=pathlib.Path,
                         required=False)
args = data_parser.parse_args()
data_dir = os.getenv('WRECKSYS_DATA_DIR') if args.data_dir is None else args.data_dir

if data_dir is None:
    data_parser.error(f"Please specify a {d.metavar} or set the WRECKSYS_DATA environment variable.")

print(f"Data Directory: {data_dir}")
dataset = GoodreadsData(data_dir)


