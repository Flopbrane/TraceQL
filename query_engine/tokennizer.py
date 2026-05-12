"""Backward-compatible parser exports.

The misspelled module name is kept temporarily so older examples keep working.
New code should import from :mod:`query_engine.parser`.
"""
from __future__ import annotations

from query_engine.parser import GRAMMAR, QuerySyntaxError, Token, TokenKind, parse, parse_query, tokenize

__all__ = [
    "GRAMMAR",
    "QuerySyntaxError",
    "Token",
    "TokenKind",
    "parse",
    "parse_query",
    "tokenize",
]
