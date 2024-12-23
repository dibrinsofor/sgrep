from src.parse_patterns import Func
from tests.utils import (
    assert_match,
    check_file
)

def test_match_def() -> None:
    assert_match("def", 
                 '''
curve_ball_def = 1234

def one() -> int:
    return 1

def two() -> int:
    return 2

def three() -> int:
    return 3''', 
                 3, Func(None, None, False))

def test_empty() -> None:
    source = expected = ""
    pattern = "def $some"

    assert_match("def $some", source, 0)