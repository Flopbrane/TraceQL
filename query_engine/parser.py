"""検索DSL文字列をASTへ変換するパーサー。"""
from __future__ import annotations

import re
from dataclasses import dataclass

from query_engine.ast import (
    AndNode,
    CompareNode,
    EmptyNode,
    FieldNode,
    NotNode,
    OrNode,
    PhraseNode,
    QueryNode,
    RegexNode,
    TermNode,
)
from query_engine.grammer import COMPARE_OPERATORS, GRAMMAR, IDENT_PATTERN, TokenKind
from query_engine.models import SearchQuery


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    value: str
    position: int


class QuerySyntaxError(ValueError):
    """検索文字列が固定文法に一致しないときに送出する例外。"""


def parse_query(text: str) -> SearchQuery:
    parser = _Parser(tokenize(text), raw_text=text)
    ast = parser.parse()
    return SearchQuery(raw_text=text, ast=ast)


def parse(text: str) -> QueryNode:
    return parse_query(text).ast


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    index = 0
    length = len(text)

    while index < length:
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char == "(":
            tokens.append(Token(TokenKind.LPAREN, char, index))
            index += 1
            continue
        if char == ")":
            tokens.append(Token(TokenKind.RPAREN, char, index))
            index += 1
            continue
        if char == ":":
            tokens.append(Token(TokenKind.COLON, char, index))
            index += 1
            continue
        if char == "~":
            tokens.append(Token(TokenKind.TILDE, char, index))
            index += 1
            continue
        if char in "<>!=":
            op = _read_operator(text, index)
            tokens.append(Token(TokenKind.OP, op, index))
            index += len(op)
            continue
        if char == '"':
            phrase, index = _read_phrase(text, index)
            tokens.append(Token(TokenKind.PHRASE, phrase, index))
            continue
        if char == "/":
            pattern, index = _read_regex(text, index)
            tokens.append(Token(TokenKind.REGEX, pattern, index))
            continue

        word_start = index
        while index < length and not text[index].isspace() and text[index] not in '():"~<>!=':
            index += 1
        tokens.append(Token(TokenKind.WORD, text[word_start:index], word_start))

    tokens.append(Token(TokenKind.EOF, "", length))
    return tokens


def _read_operator(text: str, index: int) -> str:
    two = text[index : index + 2]
    if two in COMPARE_OPERATORS:
        return two
    one = text[index]
    if one in {"<", ">"}:
        return one
    raise QuerySyntaxError(f"Invalid operator at position {index}.")


def _read_phrase(text: str, index: int) -> tuple[str, int]:
    index += 1
    chars: list[str] = []
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            chars.append(text[index + 1])
            index += 2
            continue
        if char == '"':
            return "".join(chars), index + 1
        chars.append(char)
        index += 1
    raise QuerySyntaxError("Unterminated quoted phrase.")


def _read_regex(text: str, index: int) -> tuple[str, int]:
    index += 1
    chars: list[str] = []
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            chars.extend([char, text[index + 1]])
            index += 2
            continue
        if char == "/":
            return "".join(chars), index + 1
        chars.append(char)
        index += 1
    raise QuerySyntaxError("Unterminated regex pattern.")


class _Parser:
    def __init__(self, tokens: list[Token], *, raw_text: str) -> None:
        self.tokens = tokens
        self.raw_text = raw_text
        self.index = 0

    def parse(self) -> QueryNode:
        if self._peek().kind == TokenKind.EOF:
            return EmptyNode()
        node = self._parse_or()
        self._expect(TokenKind.EOF)
        return node

    def _parse_or(self) -> QueryNode:
        node = self._parse_and()
        while self._match_word("OR"):
            node = OrNode(left=node, right=self._parse_and())
        return node

    def _parse_and(self) -> QueryNode:
        node = self._parse_not()
        while self._starts_primary() or self._match_word("AND"):
            node = AndNode(left=node, right=self._parse_not())
        return node

    def _parse_not(self) -> QueryNode:
        if self._match_word("NOT"):
            return NotNode(self._parse_not())
        token = self._peek()
        if token.kind == TokenKind.WORD and token.value.startswith("-") and len(token.value) > 1:
            self._advance()
            return NotNode(TermNode(token.value[1:]))
        return self._parse_primary()

    def _parse_primary(self) -> QueryNode:
        token = self._peek()
        if token.kind == TokenKind.LPAREN:
            self._advance()
            node = self._parse_or()
            self._expect(TokenKind.RPAREN)
            return node
        if token.kind == TokenKind.PHRASE:
            self._advance()
            return PhraseNode(token.value)
        if token.kind == TokenKind.TILDE:
            self._advance()
            return RegexNode(pattern=self._expect(TokenKind.REGEX).value)
        if token.kind != TokenKind.WORD:
            raise QuerySyntaxError(f"Expected expression at position {token.position}.")

        word = self._advance().value
        if self._match(TokenKind.COLON):
            return FieldNode(field=_validate_identifier(word), value=self._read_value())
        if self._match(TokenKind.TILDE):
            return RegexNode(field=_validate_identifier(word), pattern=self._expect(TokenKind.REGEX).value)
        if self._peek().kind == TokenKind.OP:
            operator = self._advance().value
            number = self._expect(TokenKind.WORD).value
            return CompareNode(field=_validate_identifier(word), operator=operator, value=_parse_number(number))
        compact = _parse_compact_atom(word)
        if compact is not None:
            return compact
        return TermNode(word)

    def _read_value(self) -> str:
        token = self._peek()
        if token.kind in {TokenKind.WORD, TokenKind.PHRASE}:
            return self._advance().value
        raise QuerySyntaxError(f"Expected field value at position {token.position}.")

    def _starts_primary(self) -> bool:
        token = self._peek()
        if token.kind in {TokenKind.WORD, TokenKind.PHRASE, TokenKind.LPAREN, TokenKind.TILDE}:
            if token.kind == TokenKind.WORD and token.value.upper() in {"AND", "OR"}:
                return False
            return True
        return False

    def _match_word(self, value: str) -> bool:
        token = self._peek()
        if token.kind == TokenKind.WORD and token.value.upper() == value:
            self._advance()
            return True
        return False

    def _match(self, kind: TokenKind) -> bool:
        if self._peek().kind == kind:
            self._advance()
            return True
        return False

    def _expect(self, kind: TokenKind) -> Token:
        token = self._peek()
        if token.kind != kind:
            raise QuerySyntaxError(f"Expected {kind.value} at position {token.position}.")
        return self._advance()

    def _peek(self) -> Token:
        return self.tokens[self.index]

    def _advance(self) -> Token:
        token = self.tokens[self.index]
        self.index += 1
        return token


def _parse_compact_atom(word: str) -> QueryNode | None:
    field_match = re.fullmatch(rf"({IDENT_PATTERN}):(.+)", word)
    if field_match:
        return FieldNode(field=field_match.group(1), value=field_match.group(2))
    compare_match = re.fullmatch(rf"({IDENT_PATTERN})(<=|>=|==|!=|<|>)(-?\d+(?:\.\d+)?)", word)
    if compare_match:
        return CompareNode(
            field=compare_match.group(1),
            operator=compare_match.group(2),
            value=float(compare_match.group(3)),
        )
    return None


def _validate_identifier(value: str) -> str:
    if not re.fullmatch(IDENT_PATTERN, value):
        raise QuerySyntaxError(f"Invalid field name: {value!r}.")
    return value


def _parse_number(value: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise QuerySyntaxError(f"Expected numeric value, got {value!r}.") from exc
