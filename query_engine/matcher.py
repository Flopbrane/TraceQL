"""検索DSLのASTを文書へ適用する依存なしの評価器。"""
from __future__ import annotations

import operator
import re
from typing import Any, Callable, Iterable

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
from query_engine.models import Document, SearchQuery, SearchResult
from query_engine.parser import parse_query
from query_engine.utils import flatten_text, get_path

COMPARE_FUNCS: dict[str, Callable[[float, float], bool]] = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
}


def match_query(query: str | SearchQuery | QueryNode, document: Document) -> bool:
    node = _to_node(query)
    return match_node(node, document)


def search(query: str | SearchQuery | QueryNode, documents: Iterable[Document]) -> list[SearchResult]:
    node = _to_node(query)
    return [SearchResult(document=document) for document in documents if match_node(node, document)]


def match_node(node: QueryNode, document: Document) -> bool:
    if isinstance(node, EmptyNode):
        return True
    if isinstance(node, TermNode):
        return _contains(flatten_text(document), node.term)
    if isinstance(node, PhraseNode):
        return _contains(flatten_text(document), node.phrase)
    if isinstance(node, FieldNode):
        value = get_path(document, node.field)
        return value is not None and _contains(flatten_text(value), node.value)
    if isinstance(node, CompareNode):
        value = _to_float(get_path(document, node.field))
        return value is not None and COMPARE_FUNCS[node.operator](value, node.value)
    if isinstance(node, RegexNode):
        haystack = flatten_text(document if node.field is None else get_path(document, node.field))
        return re.search(node.pattern, haystack, flags=re.IGNORECASE) is not None
    if isinstance(node, NotNode):
        return not match_node(node.child, document)
    if isinstance(node, AndNode):
        return match_node(node.left, document) and match_node(node.right, document)
    if isinstance(node, OrNode):
        return match_node(node.left, document) or match_node(node.right, document)
    raise TypeError(f"Unsupported query node: {node!r}")


def _to_node(query: str | SearchQuery | QueryNode) -> QueryNode:
    if isinstance(query, str):
        return parse_query(query).ast
    if isinstance(query, SearchQuery):
        return query.ast
    return query


def _contains(text: str, needle: str) -> bool:
    return needle.casefold() in text.casefold()


def _to_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None
