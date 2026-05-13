"""検索対象をQuery EngineのDocumentへ変換するアダプタ群。"""
from __future__ import annotations

from query_engine.adapters.browser import BrowserPage, browser_page_to_document
from query_engine.adapters.documents import TextDocument, from_text, from_text_file, normalize_text
from query_engine.adapters.extractors import extract_text_file
from query_engine.adapters.logs import log_to_document

__all__: list[str] = [
    "BrowserPage",
    "TextDocument",
    "browser_page_to_document",
    "extract_text_file",
    "from_text",
    "from_text_file",
    "log_to_document",
    "normalize_text",
]
