"""旧APIを残すための互換モジュール。

新しいコードでは query_engine.adapters.documents を使ってください。
"""
from __future__ import annotations

from query_engine.adapters.documents import TextDocument, from_text, from_text_file, normalize_text

__all__ = ["TextDocument", "from_text", "from_text_file", "normalize_text"]
