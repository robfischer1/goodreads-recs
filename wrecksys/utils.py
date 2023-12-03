import logging
import os
import pathlib
import urllib.parse
import warnings

logger = logging.getLogger(__name__)


def import_tensorflow():
    # Tensorflow has always been verbose, but the current version starts throwing warnings on import.
    # Getting this to go away is the dumbest piece of code I've ever written.
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    # logging.getLogger('tensorflow').setLevel(logging.FATAL)
    # logging.getLogger('keras').setLevel(logging.FATAL)

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        import tensorflow as tf
        import keras

    logging.info(f"Loaded: Tensorflow {tf.__version__}")
    logging.info(f"Loaded: Keras {keras.__version__}")

    return tf, keras


def display_size(size, unit=('B', 'KB', 'MB', 'GB')):
    return str(size) + unit[0] if size < 1024 else display_size(size >> 10, unit[1:])


def get_file_name(url: str) -> str:
    url_path = urllib.parse.urlparse(url).path
    file_path = pathlib.Path(url_path)
    filename = file_path.with_suffix('').stem
    return filename


def get_file_paths(url: str, dest_dir: pathlib.Path):
    file_name = get_file_name(url)
    return {
        'url': url,
        'file_name': file_name,
        'example_file': (dest_dir / f'examples/{file_name}_example.json').resolve(),
        "output_file": (dest_dir / f'raw/{file_name}.feather').resolve()
    }

def source_files(sources: dict[str, str], data_dir: pathlib.Path):
    return { k: get_file_paths(v, data_dir) for k, v in sources.items() }
