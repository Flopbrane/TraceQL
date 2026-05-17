"""Accessデータベースを検索しやすいdict/Documentへ変換するアダプタ。"""
from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any, Iterable, Sequence, cast

from query_engine.adapters.tabular import Record, rows_to_documents
from query_engine.models import Document


class AccessAdapter:
    """Accessのテーブルを、行ごとのdictとして読み込む薄いアダプタ。"""

    def __init__(self, path: str | Path, *, table: str | None = None) -> None:
        self.path = Path(path)
        self.table: str | None = table

    def load(self) -> list[Record]:
        return load_access(self.path, table=self.table)

    def documents(self) -> list[Document]:
        return access_to_documents(self.path, table=self.table)


def load_access(path: str | Path, *, table: str | None = None) -> list[Record]:
    """Accessファイルから1テーブルをlist[dict]へ変換する。
    tableを省略した場合は、最初に見つかった通常テーブルを使います。
    """
    if isinstance(path, str):
        path = Path(path)

    file_path: Path = path.expanduser().resolve()
    
    with file_path.open("rb"):
        pyodbc:Any = _import_pyodbc()
        if not hasattr(pyodbc, "connect"):
            raise RuntimeError("pyodbc module does not have connect function")
        connection_string: str = (
            "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            "DBQ="
        )
        connection: Any = pyodbc.connect(
            connection_string + str(file_path)
            )
        try:
            cursor: Any = connection.cursor()
            table_name: str = table or _first_table_name(cursor)
            cursor.execute(f"SELECT * FROM [{_escape_access_name(table_name)}]")
            columns: list[str] = [str(column[0]) for column in cursor.description]
            rows: list[Record] = [_row_to_record(columns, row) for row in cursor.fetchall()]
        finally:
            connection.close()
    return rows


def access_to_documents(path: str | Path, *, table: str | None = None) -> list[Document]:
    """Accessの各行をQuery Engineで検索できるDocumentへ変換する。"""
    database_path = Path(path)
    rows: list[Record]
    table_name: str
    rows, table_name = _load_access_with_table(database_path, table=table)
    return rows_to_documents(rows, source=str(database_path), table=table_name)


def _load_access_with_table(path: str | Path, *, table: str | None = None) -> tuple[list[Record], str]:
    database_path = Path(path)
    pyodbc: Any = _import_pyodbc()
    connection_string: str = (
        "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={database_path};"
    )
    connection: Any = pyodbc.connect(connection_string)
    try:
        cursor: Any = connection.cursor()
        table_name: str = table or _first_table_name(cursor)
        cursor.execute(f"SELECT * FROM [{_escape_access_name(table_name)}]")
        columns: list[str] = [str(column[0]) for column in cursor.description]
        return [_row_to_record(columns, row) for row in cursor.fetchall()], table_name
    finally:
        connection.close()


def _import_pyodbc() -> Any:
    try:
        return import_module("pyodbc")
    except ImportError as exc:
        raise RuntimeError("Accessを読むには pyodbc と Access ODBC Driver が必要です。") from exc


def _first_table_name(cursor: Any) -> str:
    tables_object: Any = cursor.tables(tableType="TABLE")
    for row in cast(Iterable[object], tables_object):
        name: Any | None = getattr(row, "table_name", None)
        if isinstance(name, str) and name:
            return name
    raise ValueError("Accessファイル内に通常テーブルが見つかりません。")


def _row_to_record(columns: Sequence[str], row: Any) -> Record:
    values: Sequence[Any] = cast(Sequence[Any], row)
    return {column: values[index] for index, column in enumerate(columns)}


def _escape_access_name(name: str) -> str:
    return name.replace("]", "]]")
