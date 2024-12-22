from src.parse_patterns import Tokenize, Parser, Node, SIdent, Func, Args

def parse(src: str) -> Node:
    tokens = Tokenize(src)
    parser = Parser(tokens)
    return parser.parse_commands()

# assert_eq("$*", SIdent(None, True,False, False))
def test_ident_w_wildcard() -> None:
    cmd = "$*"
    node = parse(cmd)

    assert node == SIdent("*", True, False, False)

def test_ident() -> None:
    cmd = "$sgrep"
    node = parse(cmd)

    assert node == SIdent("sgrep", False, False, False)

def test_ident_w_wildcard_pre() -> None:
    cmd = "$sgrep*"

    node = parse(cmd)
    assert node == SIdent("sgrep", False, True, False)

def test_ident_w_wildcard_post() -> None:
    cmd = "$*sgrep"
    
    node = parse(cmd)
    assert node == SIdent("sgrep", False, False, True)

def test_get_kw() -> None:
    cmd = "def"
    
    node = parse(cmd)
    assert node == Func(None, None, False)

def test_func_w_args() -> None:
    cmd = "def (args=5, ^$self)"
    
    node = parse(cmd)
    assert node == Func(None, Args(5, SIdent("self", False, False, False), []), False)