from src.parse import Func
from tests.utils import (
    assert_match,
    assert_first_match,
    check_file
)

def test_empty() -> None:
    assert_match("def $some", "", 0)

def test_wildcard_ident() -> None:
    assert_first_match("$*",
                       '''
four = 4
one = 1
two = 2
three = 3

def some():
    return "some"

class Other:
    pass''',
                    4, "four")

def test_nested_def() -> None:
    assert_first_match("def",
                       '''
class Other:
    def some():
        return "some"s''',
                    1, "some")


def test_class_match() -> None:
    assert 0 == 1
    assert_first_match("class Two",
                       '''
class Other:
    class Two:
        pass''',
                    1, "Other")

def test_match_arg_count() -> None:
    assert_first_match("def (args=2)", 
                 '''
def add(x: int, y: int) -> int:
    return x + y

def two() -> int:
    return 2''', 
                 1, "add")

def test_match_arg() -> None:
    assert_first_match("def (^$x)", 
                 '''
def square(x: int) -> int:
    return x * x

def add(x: int, y: int) -> int:
    return x + y

def two() -> int:
    return 2''', 
                 2, "square")

def test_match_arg_contains() -> None:
    assert_first_match("def ($y)", 
                 '''
def square(x: int) -> int:
    return x * x

def add(x: int, y: int) -> int:
    return x + y

def two() -> int:
    return 2''', 
                 1, "add")

def test_import():
    assert_first_match("import", '''
import some_module
''', 1, "some_module")
    
def test_match_ident_post():
    assert_first_match("$*some",
                       '''
def something(x: any) -> any:
    return "uno"
    
def wholesome():
    return ":)"
    
def some():
    pass
    
def awesome():
    return "lfggg!"''',
                       2, "wholesome")

def test_match_ident_pre():
    assert_first_match("$some*",
                       '''
def something(x: any) -> any:
    return "uno"
    
def wholesome():
    return ":)"
    
def some():
    pass''',
            2, "something")
    
def test_arg_compose_ellipsis():
    assert_first_match("call (args=3, $x, ...)", 
                       '''
add(1, add(2, 3))
format(x, y, z)''', 
                    1, "format")
    
def test_arg_compose_ellipsis():
    assert_first_match("call (args=2, $*)",
                       '''
add(1, add(2, 3))
add(1, 3)
z = add(x, y)
format(x, y, z)''',
                    4, "add")