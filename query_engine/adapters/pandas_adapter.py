"""pandas DataFrameを検索しやすいdict/Documentへ変換するアダプタ。"""
from __future__ import annotations

from typing import Any, Mapping, cast

from query_engine.adapters.tabular import Record, rows_to_documents
from query_engine.models import Document


class PandasAdapter:
    """DataFrame風オブジェクトを、行ごとのdictとして扱うアダプタ。"""

    def __init__(self, dataframe: Any, *, source: str = "pandas", table: str = "dataframe") -> None:
        self.dataframe = dataframe
        self.source = source
        self.table = table

    def load(self) -> list[Record]:
        return dataframe_to_records(self.dataframe)

    def documents(self) -> list[Document]:
        return dataframe_to_documents(self.dataframe, source=self.source, table=self.table)


def dataframe_to_records(dataframe: Any) -> list[Record]:
    """pandas.DataFrame.to_dict(orient='records') 相当でlist[dict]へ変換する。"""
    to_dict = getattr(dataframe, "to_dict", None)
    if not callable(to_dict):
        raise TypeError("dataframe must provide to_dict(orient='records').")

    records_object = to_dict(orient="records")
    if not isinstance(records_object, list):
        raise TypeError("dataframe.to_dict(orient='records') must return a list.")

    records: list[Record] = []
    for item in cast("list[object]", records_object):
        if not isinstance(item, Mapping):
            raise TypeError("Each dataframe record must be a mapping.")
        mapping = cast("Mapping[object, object]", item)
        records.append({str(key): value for key, value in mapping.items()})
    return records


def dataframe_to_documents(
    dataframe: Any,
    *,
    source: str = "pandas",
    table: str = "dataframe",
) -> list[Document]:
    """DataFrameの各行をQuery Engineで検索できるDocumentへ変換する。"""
    return rows_to_documents(dataframe_to_records(dataframe), source=source, table=table)
