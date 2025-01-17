from dataclasses import dataclass
import os
import click
from os import getcwd, path, walk
from typing import Final, Union, List, Tuple
from multiprocessing import Pool
from src.parse import SIdent, Func, Class, KW, Tokenize, Parser, Node
from src.match import MatchPatterns
from ast import AST, parse, unparse
from itertools import chain

Nodes = Union[Node, SIdent, Func, Class, KW]

PYTHON_SUFFIX: Final = ".py"
ALLOWED_SUFFIXES: Final = (PYTHON_SUFFIX, ".pyi", ".out", ".diff", ".ipynb")

CURR_DIR = getcwd()


class SgrepCommandError(Exception):
    pass


@dataclass
class Result:
    def __init__(self, filename: str, matches: list[AST]) -> None:
        self.count: int = 0
        self.pattern: str = ""
        self.matches: List[AST] = matches
        self.first_lines: List[str] = []
        self.filename: str = filename

    # TODO
    def uparse(self, node: AST) -> str:
        return unparse(node)

    def incr_count(self) -> int:
        self.count += 1
        return self.count

    def print_match(self, tree: AST) -> None:
        src = self.uparse(tree)

        # TODO move this to a util file
        # TODO conditionally apply colors based on term's capabilities
        magenta = "\033[95m"  # ]
        reset = "\033[0m"  # ]
        bold = "\033[1m"  # ]

        print(f"{bold}{magenta}{tree.lineno}:{reset} {src}")

    def flush_res(self) -> None:
        # TODO move this to a util file
        magenta = "\033[95m"  # ]
        reset = "\033[0m"  # ]
        print(f"{magenta}{self.filename}{reset}")
        list(map(self.print_match, self.matches))


def get_py_file(filepath: str) -> list[str]:
    if path.isfile(filepath):
        return [filepath]
    else:

        def get_fs(root: str, fs: list[str]) -> list[str]:
            return [path.join(root, f) for f in fs if f.endswith(ALLOWED_SUFFIXES)]

        return list(chain(*[get_fs(root, files) for root, _, files in walk(filepath)]))


def parse_command(src: str) -> Nodes:
    tokens = Tokenize(src)
    parser = Parser(tokens)
    return parser.parse_commands()


def proc_file(args: Tuple[object, str]) -> Result:
    visitor, filepath = args

    with open(filepath, "r") as f:
        src = f.read()

    tree = parse(src)

    visitor.visit(tree)

    return Result(filepath, visitor.matches)


@click.command()
@click.option("-c", "count", is_flag=True)
@click.argument("pattern", type=click.STRING, default="$*")
@click.argument("filepath", type=click.Path(exists=True), default=CURR_DIR)
def sgrep(pattern: str, filepath: str, count: bool) -> None:
    if not pattern:
        raise SgrepCommandError("Expected a pattern.")

    visitor = MatchPatterns.create(parse_command(pattern))
    files = list(get_py_file(filepath))
    processes = min(os.cpu_count() or 1, len(files))

    if processes == 1:
        match_results = [proc_file((visitor, files[0]))]
    else:
        with Pool(processes=processes) as pool:
            match_results = pool.map(proc_file, ((visitor, x) for x in files))

    if count:
        print(sum([len(x.matches) for x in match_results]))
        return

    [res.flush_res() for res in match_results]


if __name__ == "__main__":
    sgrep()
