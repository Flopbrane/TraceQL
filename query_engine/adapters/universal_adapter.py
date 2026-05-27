"""不明・壊れた入力を可能な範囲でDocumentへ変換するアダプタ。"""
from __future__ import annotations

import csv
import math
import re
from collections import Counter
from io import StringIO
from pathlib import Path

from query_engine.adapters.csv_adapter import csv_to_documents
from query_engine.adapters.documents import from_text
from query_engine.adapters.json_adapter import json_to_documents
from query_engine.adapters.tabular import Record, rows_to_documents
from query_engine.adapters.xml_adapter import xml_to_documents
from query_engine.models import Document

SORRY_MESSAGE = "Sorry I Cannot Recognize."
FALLBACK_ENCODINGS = ("utf-8", "utf-8-sig", "cp932", "shift_jis", "utf-16", "latin1")

_DATETIME_RE = re.compile(r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?\b")
_URL_RE = re.compile(r"https?://[^\s\"'<>]+")
_PATH_RE = re.compile(r"(?:[A-Za-z]:\\|/)[^\s\"'<>]+")
_KEY_VALUE_RE = re.compile(r"(?P<key>[A-Za-z_][\w.\-]*)\s*[:=]\s*(?P<value>[^,;{}\[\]\n]+)")
_PARTIAL_AST_PATTERNS = {
    "eval_call": re.compile(r"\beval\s*\("),
    "exec_call": re.compile(r"\bexec\s*\("),
    "base64_hint": re.compile(r"\b(?:atob|btoa|base64|fromCharCode)\b", re.IGNORECASE),
    "script_tag": re.compile(r"<script\b", re.IGNORECASE),
    "shell_hint": re.compile(r"\b(?:powershell|cmd\.exe|/bin/sh|curl|wget)\b", re.IGNORECASE),
}
_MAGIC_SIGNATURES: tuple[tuple[bytes, str], ...] = (
    (b"MZ", "mz_executable"),
    (b"PK\x03\x04", "zip_or_office"),
    (b"\x7fELF", "elf_executable"),
    (b"SQLite format 3\x00", "sqlite_database"),
    (b"%PDF-", "pdf"),
    (b"\xff\xd8\xff", "jpeg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
)


class UniversalAdapter:
    """既知アダプタで読めない入力を最後に受け止めるアダプタ。"""

    def __init__(self, path: str | Path, *, encoding: str = "utf-8") -> None:
        self.path = Path(path)
        self.encoding = encoding

    def documents(self) -> list[Document]:
        return universal_to_documents(self.path, encoding=self.encoding)


def universal_to_documents(path: str | Path, *, encoding: str = "utf-8") -> list[Document]:
    """不明ファイルをできるだけ検索可能なDocumentへ変換する。"""
    file_path = Path(path)
    errors: list[str] = []
    raw = file_path.read_bytes()
    binary_signals = _detect_binary_signals(raw)
    entropy_score = _entropy_score(raw)

    for loader in (_try_json, _try_xml, _try_csv):
        try:
            documents = loader(file_path, encoding=encoding)
        except Exception as exc:  # noqa: BLE001 - fallback adapter keeps parse errors as evidence.
            errors.append(f"{loader.__name__}: {exc}")
            continue
        if documents:
            return [
                _with_universal_metadata(
                    document,
                    "known_adapter",
                    1.0,
                    [],
                    errors,
                    encoding=encoding,
                    entropy_score=entropy_score,
                    binary_signals=binary_signals,
                )
                for document in documents
            ]

    try:
        text, detected_encoding, decode_errors = _read_text_with_fallback(raw, preferred_encoding=encoding)
        errors.extend(decode_errors)
    except Exception as exc:  # noqa: BLE001
        return [_unrecognized_document(file_path, errors + [f"read_text: {exc}"], entropy_score, binary_signals)]

    if not text.strip():
        return [_unrecognized_document(file_path, errors + ["empty text"], entropy_score, binary_signals)]

    rows = _infer_records(text)
    signals = _detect_signals(text, binary_signals=binary_signals, entropy_score=entropy_score)
    partial_ast_signals = _detect_partial_ast_signals(text)
    if rows:
        confidence = _confidence_score(
            strategy="inferred_records",
            signals=signals,
            entropy_score=entropy_score,
            field_consistency=_field_consistency(rows),
        )
        return [
            _with_universal_metadata(
                document,
                "inferred_records",
                confidence,
                signals,
                errors,
                encoding=detected_encoding,
                entropy_score=entropy_score,
                binary_signals=binary_signals,
                partial_ast_signals=partial_ast_signals,
            )
            for document in rows_to_documents(rows, source=str(file_path), table=file_path.stem)
        ]

    if signals or len(text.strip()) >= 20:
        confidence = _confidence_score(
            strategy="plain_text",
            signals=signals,
            entropy_score=entropy_score,
            field_consistency=0.0,
        )
        text_document = from_text(
            text,
            title=file_path.stem,
            source=str(file_path),
            format="unknown",
            confidence=confidence,
            signals=signals,
            parse_errors=errors,
            encoding=detected_encoding,
            entropy_score=entropy_score,
            binary_signals=binary_signals,
            partial_ast_signals=partial_ast_signals,
        )
        return [text_document.to_document()]

    return [_unrecognized_document(file_path, errors, entropy_score, binary_signals)]


def _try_json(path: Path, *, encoding: str) -> list[Document]:
    if path.suffix.casefold() not in {".json", ".jsonl"}:
        return []
    return json_to_documents(path)


def _try_xml(path: Path, *, encoding: str) -> list[Document]:
    if path.suffix.casefold() not in {".xml", ".xhtml", ".rss", ".atom"}:
        return []
    return xml_to_documents(path, encoding=encoding)


def _try_csv(path: Path, *, encoding: str) -> list[Document]:
    if path.suffix.casefold() not in {".csv", ".tsv", ".tab"}:
        return []
    return csv_to_documents(path, encoding=encoding)


def _infer_records(text: str) -> list[Record]:
    rows = _infer_key_value_rows(text)
    if rows:
        return rows
    rows = _infer_delimited_rows(text)
    if rows:
        return rows
    return []


def _infer_key_value_rows(text: str) -> list[Record]:
    rows: list[Record] = []
    for index, line in enumerate(text.splitlines(), start=1):
        pairs = {
            match.group("key"): match.group("value").strip().strip("\"'")
            for match in _KEY_VALUE_RE.finditer(line)
        }
        if pairs:
            pairs["line_number"] = index
            pairs["raw_line"] = line.strip()
            rows.append(pairs)
    return rows


def _infer_delimited_rows(text: str) -> list[Record]:
    sample = "\n".join(line for line in text.splitlines()[:20] if line.strip())
    if not sample:
        return []
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
    except csv.Error:
        return []
    reader = csv.DictReader(StringIO(text), dialect=dialect)
    if not reader.fieldnames:
        return []
    return [
        {str(key): value for key, value in row.items() if key is not None}
        for row in reader
    ]


def _read_text_with_fallback(raw: bytes, *, preferred_encoding: str) -> tuple[str, str, list[str]]:
    errors: list[str] = []
    encodings = tuple(dict.fromkeys((preferred_encoding, *FALLBACK_ENCODINGS)))
    for candidate in encodings:
        try:
            return raw.decode(candidate), candidate, errors
        except UnicodeDecodeError as exc:
            errors.append(f"decode:{candidate}: {exc}")
    return raw.decode(preferred_encoding, errors="replace"), f"{preferred_encoding}+replace", errors


def _detect_binary_signals(raw: bytes) -> list[str]:
    signals = [name for signature, name in _MAGIC_SIGNATURES if raw.startswith(signature)]
    if b"\x00" in raw[:4096]:
        signals.append("contains_nul_bytes")
    return signals


def _entropy_score(raw: bytes) -> float:
    if not raw:
        return 0.0
    counts = Counter(raw)
    length = len(raw)
    entropy = -sum((count / length) * math.log2(count / length) for count in counts.values())
    return round(entropy, 4)


def _detect_signals(text: str, *, binary_signals: list[str], entropy_score: float) -> list[str]:
    signals: list[str] = []
    if _DATETIME_RE.search(text):
        signals.append("datetime")
    if _URL_RE.search(text):
        signals.append("url")
    if _PATH_RE.search(text):
        signals.append("file_path")
    if _KEY_VALUE_RE.search(text):
        signals.append("key_value_pairs")
    if "{" in text or "[" in text:
        signals.append("json_like")
    if "<" in text and ">" in text:
        signals.append("xml_like")
    if entropy_score >= 7.2:
        signals.append("high_entropy")
    signals.extend(binary_signals)
    return signals


def _detect_partial_ast_signals(text: str) -> list[str]:
    return [name for name, pattern in _PARTIAL_AST_PATTERNS.items() if pattern.search(text)]


def _field_consistency(rows: list[Record]) -> float:
    if len(rows) < 2:
        return 0.5 if rows else 0.0
    key_sets = [set(row.keys()) - {"line_number", "raw_line"} for row in rows]
    common = set.intersection(*key_sets) if key_sets else set()
    union = set.union(*key_sets) if key_sets else set()
    if not union:
        return 0.0
    return len(common) / len(union)


def _confidence_score(
    *,
    strategy: str,
    signals: list[str],
    entropy_score: float,
    field_consistency: float,
) -> float:
    base = 0.35 if strategy == "plain_text" else 0.50
    base += min(len(signals), 5) * 0.03
    base += field_consistency * 0.20
    if entropy_score >= 7.2:
        base -= 0.15
    return round(max(0.05, min(base, 0.95)), 2)


def _with_universal_metadata(
    document: Document,
    strategy: str,
    confidence: float,
    signals: list[str],
    errors: list[str],
    *,
    encoding: str,
    entropy_score: float,
    binary_signals: list[str],
    partial_ast_signals: list[str] | None = None,
) -> Document:
    metadata = dict(document.get("metadata", {})) if isinstance(document.get("metadata"), dict) else {}
    metadata.update(
        {
            "adapter": "universal",
            "strategy": strategy,
            "confidence": confidence,
            "signals": signals,
            "encoding": encoding,
            "entropy_score": entropy_score,
            "binary_signals": binary_signals,
            "partial_ast_signals": partial_ast_signals or [],
            "parse_errors": errors,
        }
    )
    return {**dict(document), "metadata": metadata}


def _unrecognized_document(
    path: Path,
    errors: list[str],
    entropy_score: float,
    binary_signals: list[str],
) -> Document:
    return {
        "title": SORRY_MESSAGE,
        "text": SORRY_MESSAGE,
        "source": str(path),
        "metadata": {
            "adapter": "universal",
            "strategy": "unrecognized",
            "confidence": 0.0,
            "signals": binary_signals,
            "encoding": "",
            "entropy_score": entropy_score,
            "binary_signals": binary_signals,
            "partial_ast_signals": [],
            "parse_errors": errors,
        },
    }
