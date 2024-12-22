from tests.utils import (
    assert_match,
    check_file
)

def test_match_def() -> None:
    check_file("match_def", "def")

def test_empty() -> None:
    source = expected = ""
    pattern = "def $some"

    assert_match("def $some", source, expected)