"""grammar.py への互換エイリアス。

先生の作業中ファイル名として使われていた grammar.py からも読めるように、
正式な query_engine.grammar を再公開します。
"""
from __future__ import annotations

from query_engine.grammar import COMPARE_OPERATORS, GRAMMAR, GRAMMAR_EBNF, IDENT_PATTERN, LOGICAL_OPERATORS, TokenKind

__all__: list[str] = [
    "COMPARE_OPERATORS",
    "GRAMMAR",
    "GRAMMAR_EBNF",
    "IDENT_PATTERN",
    "LOGICAL_OPERATORS",
    "TokenKind",
]
