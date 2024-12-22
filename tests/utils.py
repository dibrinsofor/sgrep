from pathlib import Path
from typing import List, Tuple, Union, Never


PYTHON_SUFFIX = ".py"
ALLOWED_SUFFIXES = (PYTHON_SUFFIX, ".pyi", ".out", ".diff", ".ipynb")


THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR / "data"
PROJECT_ROOT = THIS_DIR.parent


def assert_match(pattern: str, src: str, out: str) -> None:
    assert find_match(pattern, src) == out

def check_file(filepath: str, pattern: str) -> None:
    with open(DATA_DIR / filepath, "r") as f:
        lines = f.read()

    test = lines.split("# output", 1)

    assert len(test) == 2, "Only source and output expected"

    case = test[0].strip()
    expected = test[1].strip()

    assert_match(pattern, case, expected)