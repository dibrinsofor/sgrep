from pathlib import Path
from parse import Tokenize, Parser, Node, SIdent, Func, Class
from src.match import MatchPatterns
import ast
from typing import Optional, Union


PYTHON_SUFFIX = ".py"
ALLOWED_SUFFIXES = (PYTHON_SUFFIX, ".pyi", ".out", ".diff", ".ipynb")


THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR / "data"
PROJECT_ROOT = THIS_DIR.parent

Nodes = Union[SIdent, Func, Class]

def parse(src: str) -> Nodes:
    tokens = Tokenize(src)
    parser = Parser(tokens)
    return parser.parse_commands()

def assert_match(cmd: str, src: str, expected_matches: int, first: Optional[ast.AST] = None) -> None:
    node = parse(cmd)

    visitor = MatchPatterns.create(node)
    visitor.visit(ast.parse(src))

    assert len(visitor.matches) == expected_matches
    assert visitor.matches[0] == first

def assert_parse(cmd: str, expected: Node) -> None:
    node = parse(cmd)

    assert node == SIdent("*", True, False, False)

def check_file(filepath: str, pattern: str) -> None:
    with open(DATA_DIR / filepath, "r") as f:
        lines = f.read()

    test = lines.split("# output", 1)

    assert len(test) == 2, "Only source and output expected"

    case = test[0].strip()
    expected = test[1].strip()

    assert_match(pattern, case, expected)