"""Query Engine: 構造化された文章検索DSL。"""
from __future__ import annotations

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
from query_engine.matcher import match_query, search
from query_engine.models import SearchQuery, SearchResult, SortSpec
from query_engine.parser import GRAMMAR, QuerySyntaxError, parse, parse_query, tokenize
from query_engine.documents import TextDocument, from_text, from_text_file, normalize_text

__all__ = [
    "AndNode",
    "CompareNode",
    "EmptyNode",
    "FieldNode",
    "GRAMMAR",
    "NotNode",
    "OrNode",
    "PhraseNode",
    "QueryNode",
    "QuerySyntaxError",
    "RegexNode",
    "SearchQuery",
    "SearchResult",
    "SortSpec",
    "TermNode",
    "TextDocument",
    "from_text",
    "from_text_file",
    "match_query",
    "normalize_text",
    "parse",
    "parse_query",
    "search",
    "tokenize",
]
