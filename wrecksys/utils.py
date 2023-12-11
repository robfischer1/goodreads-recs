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

def in_notebook() -> bool:
    try:
        get_ipython = sys.modules['IPython'].get_ipython
        if 'google.colab' in str(get_ipython()):
            return True
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True
        elif shell == 'TerminalInteractiveShell':
            return False
        else:
            return False
    except NameError:
        return False


def check_memory() -> tuple[float, dict]:
    """https://stackoverflow.com/a/75013631"""
    # These are the usual ipython objects, including this one you are creating
    ipython_vars = ["In", "Out", "exit", "quit", "get_ipython", "ipython_vars"]

    # Get a sorted list of the objects and their sizes
    mem = {
        key: value
        for key, value in sorted(
            [
                (x, sys.getsizeof(globals().get(x)))
                for x in dir()
                if not x.startswith("_") and x not in sys.modules and x not in ipython_vars
            ],
            key=lambda x: x[1],
            reverse=True,
        )
    }

    total = 0
    for k, v in mem.items():
        total += v
        print(f"{k}: {display_size(v)}")

    total /= 1e6

    return total, mem