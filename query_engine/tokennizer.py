"""tokenizer.py への互換エイリアス。

古い綴りのimportを一時的に残します。新しいコードでは
query_engine.tokenizer を使ってください。
"""
from __future__ import annotations

from query_engine.tokenizer import GRAMMAR, QuerySyntaxError, Token, TokenKind, parse, parse_query, tokenize

__all__ = [
    "GRAMMAR",
    "QuerySyntaxError",
    "Token",
    "TokenKind",
    "parse",
    "parse_query",
    "tokenize",
]
