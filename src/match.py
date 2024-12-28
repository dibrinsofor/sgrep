from dataclasses import dataclass
from src.parse import Func, SIdent, Class, Args, Node, KW
from typing import Any, List, Dict, TypeVar, Generic, Union, overload, Tuple
import ast

Nodes = Union[Node, SIdent, Func, Class, KW]

class SgrepMatchError(Exception):
    pass

T = TypeVar("T")

class MatchPatterns(Generic[T]):
    _registry: Dict[str, T] = {}

    @classmethod
    def register(cls, pattern: str, visitor_cls: T) -> None:
        cls._registry[pattern] = visitor_cls

    @classmethod
    def create(cls, pattern: Nodes) -> T:
        pattern_type: str = pattern.__class__.__name__
        visitor_cls = cls._registry.get(pattern_type)
        if not visitor_cls:
            raise ValueError(f"Pattern not Implemented: {pattern}")
        return visitor_cls(pattern) #type: ignore

class MatchPatternIdent(ast.NodeVisitor):
    def __init__(self, pattern: SIdent):
        self.pattern = pattern
        self.matches: List[ast.AST] = []

    def is_ident_match(self, ident: SIdent, node: ast.Name) -> bool:
        return ident.is_wildcard or ident.name in node.id

    def visit_Name(self, node: ast.Name) -> None:
        if self.is_ident_match(self.pattern, node):
            self.matches.append(node)

class MatchPatternFunc(ast.NodeVisitor):
    def __init__(self, pattern: Func):
        self.pattern = pattern
        self.matches: List[ast.AST] = []

    @overload
    def is_ident_match(self, ident: SIdent, node: ast.FunctionDef) -> bool: ...
    @overload
    def is_ident_match(self, ident: SIdent, node: ast.arg) -> bool: ...
    def is_ident_match(self, ident: SIdent, node: Any) -> bool:
        if isinstance(node, ast.FunctionDef):
            return ident.is_wildcard or ident.name in node.name
        elif isinstance(node, ast.arg):
            return ident.is_wildcard or ident.name in node.arg
        else:
            raise SgrepMatchError("Match case not accounted for.")
    
    def is_arg_match(self, args: Args, node: ast.FunctionDef) -> bool:
        if args.count and not args.first_arg and len(args.contains) == 0:
            return len(node.args.args) == args.count
        
        if args.count and len(node.args.args) != args.count:
                return False
            
        if args.first_arg and 1 <= len(node.args.args):
            if not self.is_ident_match(args.first_arg, node.args.args[0]):
                return False
            
        for arg in args.contains:
            exists = False
            for exp in node.args.args:
                if self.is_ident_match(arg, exp):
                    exists = True

            if not exists:
                return False
        
        return True
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        fname = self.pattern.fname
        args = self.pattern.args
        local_matches = set()

        if not fname and not args:
            self.matches.append(node)
            return
        
        # some* or *some or some
        if fname and self.is_ident_match(fname, node):
            local_matches.add(node)

        if args and self.is_arg_match(args, node):
            local_matches.add(node)

        if bool(local_matches):
            self.matches.extend(local_matches)

class MatchPatternClass(ast.NodeVisitor):
    def __init__(self, pattern: Class):
        self.pattern = pattern
        self.matches: List[ast.AST] = []

    def is_ident_match(self, ident: SIdent, node: ast.ClassDef) -> bool:
        return ident.is_wildcard or ident.name in node.name
        
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        cname = self.pattern.cname
        local_matches = set()

        if cname and self.is_ident_match(cname, node):
            local_matches.add(node)
        elif not cname:
            local_matches.add(node)

        if bool(local_matches):
            self.matches.extend(local_matches)

MatchPatterns.register("SIdent", MatchPatternIdent)
MatchPatterns.register("Func", MatchPatternFunc)
MatchPatterns.register("Class", MatchPatternClass)
# MatchPatterns.register(Keyword, MatchKeyword)




