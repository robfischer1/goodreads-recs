import importlib
import importlib.util
import logging
import os
import pathlib
import sys
import types
import urllib.parse
import warnings

logger = logging.getLogger(__name__)


def import_tensorflow() -> tuple[types.ModuleType, types.ModuleType]:
    # Tensorflow has always been verbose, but the current version starts throwing warnings on import.
    # Getting this to go away is the dumbest piece of code I've ever written.
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    return _silent_import('tensorflow'), _silent_import('keras')


def _silent_import(module_name: str) -> types.ModuleType:
    if module_name in sys.modules:
        return sys.modules[module_name]
    elif (spec := importlib.util.find_spec(module_name)) is not None:
        logging.getLogger(module_name).setLevel(logging.FATAL)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            logging.info(f"Loaded: {module_name.title()} {module.__version__}")
            return module


def display_size(size: int, unit=('B', 'KB', 'MB', 'GB')) -> str:
    return str(size) + unit[0] if size < 1024 else display_size(size >> 10, unit[1:])


def get_file_name(url: str) -> str:
    url_path = urllib.parse.urlparse(url).path
    file_path = pathlib.Path(url_path)
    filename = file_path.with_suffix('').stem
    return filename


def get_file_paths(url: str, dest_dir: pathlib.Path) -> dict:
    file_name = get_file_name(url)
    return {
        'url': url,
        'file_name': file_name,
        'example_file': (dest_dir / f'examples/{file_name}_example.json').resolve(),
        "output_file": (dest_dir / f'raw/{file_name}.feather').resolve()
    }

def source_files(sources: dict[str, str], data_dir: pathlib.Path) -> dict:
    return { k: get_file_paths(v, data_dir) for k, v in sources.items() }
