import keyword
from dataclasses import dataclass
from enum import Enum, auto
from typing import Final, Optional, Any, List


class Type(Enum):
    KEYWORD = auto()
    LPAREN = auto()
    RPAREN = auto()
    EQUALS = auto()
    COMMA = auto()
    CARET = auto()
    DECORATOR = auto()
    DOTS = auto()
    SIGIL = auto()
    NUM = auto()


TOKENMAPPING: Final = {
    "(": Type.LPAREN,
    ")": Type.RPAREN,
    "=": Type.EQUALS,
    ",": Type.COMMA,
    "^": Type.CARET,
    "@": Type.DECORATOR,
    "...": Type.DOTS,
    "$": Type.SIGIL,
}

KEYWORDS: Final = keyword.kwlist + ["call", "args"]


@dataclass
class Token:
    type: Type
    value: str
    column: int


@dataclass
class Node:
    pass


@dataclass
class SIdent(Node):
    name: str
    is_wildcard: bool
    has_prefix: bool
    has_suffix: bool


@dataclass
class Args:
    count: Optional[int]
    first_arg: Optional[SIdent]
    contains: List[SIdent]


@dataclass
class Func(Node):
    fname: Optional[SIdent]
    args: Optional[Args]
    call: bool


@dataclass
class Class(Node):
    cname: Optional[SIdent]
    inherits: List[SIdent]


@dataclass
class KW(Node):
    kw: str
    ctx: Optional[Any]  # TODO: Figure ctx out to track for KW


class SgrepParseError(Exception):
    pass


class Tokenize:
    def __init__(self, command: str):
        if not command:
            raise SgrepParseError("Expected command.")
        self.cmd = command
        self.pos = 0
        self.current_char = command[0]
        self.column = 1
        self.keywords = KEYWORDS

    def advance(self) -> None:
        self.pos += 1
        if self.pos >= len(self.cmd):
            self.current_char = None
        else:
            self.current_char = self.cmd[self.pos]
            self.column += 1

    def consume_wspace(self) -> None:
        while self.current_char and self.current_char.isspace():
            self.advance()

    def get_ident(self) -> str:
        result = ""

        while self.current_char and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            result += self.current_char
            self.advance()

        return result

    def get_sigil_sym(self) -> Token:
        start = self.column
        self.advance()  # Skip $

        if not self.current_char:
            raise SgrepParseError("Unexpected end after $")

        has_prefix = self.current_char == "*"
        if has_prefix:
            self.advance()
            if not self.current_char:
                return Token(Type.SIGIL, "$*", start)  # Handle bare $* wildcard

        id = (
            self.get_ident()
            if self.current_char
            and (self.current_char.isalpha() or self.current_char == "_")
            else ""
        )

        if keyword.iskeyword(id):
            raise SgrepParseError(f"Expected identifier, got keyword '{id}'")

        has_suffix = self.current_char == "*" if self.current_char else False
        if has_suffix:
            self.advance()

        result = f"${'*' if has_prefix else ''}{id}{'*' if has_suffix else ''}"
        return Token(Type.SIGIL, result, start)

    def get_next_token(self) -> Optional[Token]:
        while self.current_char:
            # if self.current_char == "a":
            #     breakpoint()
            if self.current_char.isspace():
                self.consume_wspace()
                continue
            if self.current_char.isnumeric():
                start = self.column
                num = self.current_char
                self.advance()
                return Token(Type.NUM, num, start)
            if self.current_char == "$":
                return self.get_sigil_sym()
            if self.current_char.isalpha() or self.current_char == "_":
                start = self.column
                id = self.get_ident()

                if id in self.keywords:
                    return Token(Type.KEYWORD, id, start)

                raise SgrepParseError(
                    f"Trailing char(s), {id}. Expected keywords or sigil ident"
                )
            if self.current_char == ".":
                start = self.column
                result = ""
                while self.current_char == ".":
                    result += "."
                    self.advance()
                if len(result) == 3:
                    return Token(TOKENMAPPING[result], result, start)
                else:
                    raise SgrepParseError("Invalid command.")
            if self.current_char in TOKENMAPPING:
                start = self.column
                char = self.current_char
                self.advance()
                return Token(TOKENMAPPING[char], char, start)

        return None


class Parser:
    def __init__(self, tokens: Tokenize):
        self.tokens = tokens
        self.current_token = self.tokens.get_next_token()

    def consume(self, token_type: Type) -> None:
        if self.current_token and self.current_token.type == token_type:
            self.current_token = self.tokens.get_next_token()
        else:
            raise SgrepParseError("Invalid command.")

    def parse_arg_count(self) -> int:
        self.consume(Type.KEYWORD)

        if self.current_token and self.current_token.type == Type.EQUALS:
            self.consume(Type.EQUALS)
            if self.current_token.type == Type.NUM:
                count = int(self.current_token.value)
                self.consume(Type.NUM)
                return count

        raise SgrepParseError("Invalid command.")

    def parse_args(self) -> Args:
        count: Optional[int] = None
        first: Optional[SIdent] = None
        contains: List[SIdent] = []

        self.consume(Type.LPAREN)

        while self.current_token and self.current_token.type != Type.RPAREN:
            if self.current_token.type == Type.KEYWORD:
                if self.current_token.value == "args":
                    count = self.parse_arg_count()
                else:
                    raise SgrepParseError("Invalid command.")
            elif self.current_token.type == Type.CARET:
                self.consume(Type.CARET)
                if self.current_token.type == Type.SIGIL:
                    first = self.parse_sigil_ident()
                else:
                    raise SgrepParseError("Invalid command.")
            elif self.current_token.type == Type.SIGIL:
                contains.extend(self.parse_sigil_ident())
            elif self.current_token.type == Type.DOTS:
                self.consume(Type.DOTS)

            if self.current_token and self.current_token.type == Type.COMMA:
                self.consume(Type.COMMA)

        self.consume(Type.RPAREN)

        return Args(count, first, contains)

    def parse_sigil_ident(self) -> SIdent:
        token = self.current_token
        self.consume(Type.SIGIL)
        value = token.value[1:]  # Remove $

        is_wildcard = value == "*"
        has_suffix = not is_wildcard and value.startswith("*")
        has_prefix = not is_wildcard and value.endswith("*")

        if has_prefix or has_suffix:
            value = value.strip("*")

        return SIdent(value, is_wildcard, has_prefix, has_suffix)

    def parse_commands(self) -> Node:
        token = self.current_token

        while token:
            match token.type:
                case Type.KEYWORD:
                    if token.value == "def":
                        name: Optional[SIdent] = None
                        args: Optional[Args] = None

                        self.consume(Type.KEYWORD)

                        if self.current_token and self.current_token.type == Type.SIGIL:
                            name = self.parse_sigil_ident()

                        if (
                            self.current_token
                            and self.current_token.type == Type.LPAREN
                        ):
                            args = self.parse_args()

                        return Func(name, args, False)

                    elif token.value == "class":
                        name: Optional[SIdent] = None
                        inherits: List[SIdent] = []

                        if self.current_token and self.current_token.type == Type.SIGIL:
                            name = self.parse_sigil_ident()

                        return Class(name, inherits)

                    elif token.value == "call":
                        name: Optional[SIdent] = None
                        args: Optional[Args] = None

                        if self.current_token and self.current_token.type == Type.SIGIL:
                            name = self.parse_sigil_ident()

                        if (
                            self.current_token
                            and self.current_token.type == Type.LPAREN
                        ):
                            args = self.parse_args()

                        return Func(name, args, True)
                    else:
                        return KW(token.value, None)
                case Type.SIGIL:
                    return self.parse_sigil_ident()
                case Type.DECORATOR:
                    pass

        raise SgrepParseError("Invalid command.")

