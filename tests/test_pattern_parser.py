from src.parse_patterns import SIdent, Func, Args
from .utils import assert_parse

def test_ident_w_wildcard() -> None:
    assert_parse("$*", SIdent("*", True, False, False))

def test_ident() -> None:
    assert_parse("$sgrep", SIdent("sgrep", False, False, False))

def test_ident_w_wildcard_pre() -> None:
    assert_parse("$sgrep*", SIdent("sgrep", False, True, False))

def test_ident_w_wildcard_post() -> None:
    assert_parse("$*sgrep", SIdent("sgrep", False, False, True))

def test_get_kw() -> None:
    assert_parse("def", Func(None, None, False))

def test_func_w_args() -> None:
    assert_parse("def (args=5, ^$self)", Func(None, Args(5, SIdent("self", False, False, False), []), False))