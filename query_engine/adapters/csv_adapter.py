"""CSVを検索しやすいdict/Documentへ変換するアダプタ。"""
from __future__ import annotations

import csv
from pathlib import Path

from query_engine.adapters.tabular import Record, rows_to_documents
from query_engine.models import Document


class CsvAdapter:
    """CSVファイルを、行ごとのdictとして読み込む小さなアダプタ。"""

    def __init__(self, path: str | Path, *, encoding: str = "utf-8-sig") -> None:
        self.path = Path(path)
        self.encoding = encoding

    def load(self) -> list[Record]:
        return load_csv(self.path, encoding=self.encoding)

    def documents(self) -> list[Document]:
        return csv_to_documents(self.path, encoding=self.encoding)


def load_csv(path: str | Path, *, encoding: str = "utf-8-sig") -> list[Record]:
    """CSVをlist[dict]へ変換する。先頭行を列名として扱う。"""
    csv_path = Path(path)
    with csv_path.open("r", encoding=encoding, newline="") as file:
        reader = csv.DictReader(file)
        return [
            {str(key): value for key, value in row.items() if key is not None}
            for row in reader
        ]


def csv_to_documents(path: str | Path, *, encoding: str = "utf-8-sig") -> list[Document]:
    """CSVの各行をQuery Engineで検索できるDocumentへ変換する。"""
    csv_path = Path(path)
    return rows_to_documents(load_csv(csv_path, encoding=encoding), source=str(csv_path), table=csv_path.stem)
