from dataclasses import dataclass, field
import os
import click
from os import getcwd, path, walk
from typing import Generator, Final, Union, List, Tuple
from multiprocessing import Pool
from src.parse import SIdent, Func, Class, KW, Tokenize, Parser, Node
from src.match import MatchPatterns
import ast

Nodes = Union[Node, SIdent, Func, Class, KW]

PYTHON_SUFFIX: Final = ".py"
ALLOWED_SUFFIXES: Final = (PYTHON_SUFFIX, ".pyi", ".out", ".diff", ".ipynb")

CURR_DIR = getcwd()


class SgrepCommandError(Exception):
    pass


@dataclass
class Result:
    count: int = 0
    pattern: str = ""
    matches: List[ast.AST] = field(default_factory=list)
    first_lines: List[str] = field(default_factory=list)
    filename: str = ""

    def unparse(self, node: ast.AST) -> str:
        return ast.unparse(node)

    def incr_count(self) -> int:
        self.count += 1
        return self.count

    def print_match(self, tree: ast.AST) -> None:
        src = self.unparse(tree)
        # TODO move this to a util file
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


def get_py_file(filepath: str) -> Generator[str, None, None]:
    if path.isfile(filepath):
        yield filepath
    else:
        for root, dirs, files in walk(filepath, topdown=True):
            dirs[:] = [d for d in dirs if d not in [".git", ".venv"]]
            for file in files:
                if file.endswith(ALLOWED_SUFFIXES):
                    yield path.join(root, file)


def parse_command(src: str) -> Nodes:
    tokens = Tokenize(src)
    parser = Parser(tokens)
    return parser.parse_commands()


def proc_file(args: Tuple[object, str]) -> Result:
    visitor, filepath = args

    res = Result()
    res.filename = filepath

    with open(filepath, "r") as f:
        src = f.read()

    tree = ast.parse(src)
    visitor.visit(tree)

    res.matches = visitor.matches

    return res


@click.command()
@click.option("-c", "count", is_flag=True)
@click.argument("pattern", type=click.STRING, default="$*")
@click.argument("filepath", type=click.Path(exists=True), default=CURR_DIR)
def sgrep(pattern: str, filepath: str, count: bool) -> None:
    if not pattern:
        raise SgrepCommandError("Expected a pattern.")

    cmd = parse_command(pattern)
    visitor = MatchPatterns.create(cmd)

    processes = os.cpu_count() or 1
    with Pool(processes=processes) as pool:
        match_results = pool.map(
            proc_file, ((visitor, x) for x in get_py_file(filepath))
        )

    if count:
        print(sum([len(x.matches) for x in match_results]))
        return

    [res.flush_res() for res in match_results]


if __name__ == "__main__":
    sgrep()
