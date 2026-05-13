"""ブラウザ由来のページ情報をDocumentへ変換するアダプタ。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from query_engine.adapters.documents import normalize_text
from query_engine.models import Document


@dataclass(frozen=True, slots=True)
class BrowserPage:
    """ブラウザ検索で扱うページ情報の標準形。"""

    title: str
    url: str
    text: str = ""
    visited_at: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


def browser_page_to_document(page: BrowserPage) -> Document:
    """BrowserPageを検索用Documentへ変換する。"""
    metadata = dict(page.metadata)
    if page.visited_at is not None:
        metadata["visited_at"] = page.visited_at
    return {
        "title": page.title,
        "url": page.url,
        "text": normalize_text(page.text),
        "metadata": metadata,
    }
