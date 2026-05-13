"""Query Engine: 構造化された文章検索DSL。"""
from __future__ import annotations

from query_engine.adapters import (
    BrowserPage,
    TextDocument,
    browser_page_to_document,
    extract_text_file,
    from_text,
    from_text_file,
    log_to_document,
    normalize_text,
)
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
from query_engine.evaluators.memory import match_query, search
from query_engine.evaluators.sql import SqlCompileResult, compile_sql_where
from query_engine.models import SearchQuery, SearchResult, SortSpec
from query_engine.parser import GRAMMAR, QuerySyntaxError, parse, parse_query, tokenize

__all__: list[str] = [
    "AndNode",
    "BrowserPage",
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
    "SqlCompileResult",
    "SortSpec",
    "TermNode",
    "TextDocument",
    "browser_page_to_document",
    "compile_sql_where",
    "extract_text_file",
    "from_text",
    "from_text_file",
    "log_to_document",
    "match_query",
    "normalize_text",
    "parse",
    "parse_query",
    "search",
    "tokenize",
]
