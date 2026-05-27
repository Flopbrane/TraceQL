"""XMLを検索しやすいdict/Documentへ変換するアダプタ。"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from query_engine.adapters.tabular import Record, rows_to_documents
from query_engine.models import Document


class XmlAdapter:
    """XMLファイルを、要素ごとのdictとして読み込む小さなアダプタ。"""

    def __init__(self, path: str | Path, *, encoding: str = "utf-8") -> None:
        self.path = Path(path)
        self.encoding = encoding

    def load(self) -> list[Record]:
        return load_xml(self.path, encoding=self.encoding)

    def documents(self) -> list[Document]:
        return xml_to_documents(self.path, encoding=self.encoding)


def load_xml(path: str | Path, *, encoding: str = "utf-8") -> list[Record]:
    """XMLを要素ごとのlist[dict]へ変換する。"""
    xml_path = Path(path)
    root = ET.fromstring(xml_path.read_text(encoding=encoding))
    rows: list[Record] = []
    _walk_element(root, rows, path=_strip_namespace(root.tag), depth=0)
    return rows


def xml_to_documents(path: str | Path, *, encoding: str = "utf-8") -> list[Document]:
    """XMLの各要素をQuery Engineで検索できるDocumentへ変換する。"""
    xml_path = Path(path)
    return rows_to_documents(
        load_xml(xml_path, encoding=encoding),
        source=str(xml_path),
        table=xml_path.stem,
    )


def _walk_element(element: ET.Element, rows: list[Record], *, path: str, depth: int) -> None:
    text = _element_text(element)
    attributes = { _strip_namespace(key): value for key, value in element.attrib.items() }
    row: Record = {
        "tag": _strip_namespace(element.tag),
        "path": path,
        "depth": depth,
        "text": text,
        "attributes": attributes,
        "children": [_strip_namespace(child.tag) for child in list(element)],
    }

    for key, value in attributes.items():
        if key not in row:
            row[key] = value

    rows.append(row)

    child_counts: dict[str, int] = {}
    for child in list(element):
        child_tag = _strip_namespace(child.tag)
        child_counts[child_tag] = child_counts.get(child_tag, 0) + 1
        child_path = f"{path}/{child_tag}[{child_counts[child_tag]}]"
        _walk_element(child, rows, path=child_path, depth=depth + 1)


def _element_text(element: ET.Element) -> str:
    parts = [part.strip() for part in element.itertext() if part and part.strip()]
    return " ".join(parts)


def _strip_namespace(name: str) -> str:
    if "}" in name:
        return name.rsplit("}", 1)[1]
    return name
