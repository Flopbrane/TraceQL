import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from query_engine.adapters.csv_adapter import CsvAdapter, load_csv
from query_engine.adapters.json_adapter import JsonAdapter, load_json
from query_engine.adapters.pandas_adapter import PandasAdapter
from query_engine.adapters.tabular import row_to_document
from query_engine.evaluators.memory import match_query


class FakeDataFrame:
    def __init__(self, records: list[dict[str, Any]]) -> None:
        self.records = records

    def to_dict(self, *, orient: str) -> list[dict[str, Any]]:
        if orient != "records":
            raise ValueError(orient)
        return self.records


class TableAdapterTests(unittest.TestCase):
    def test_csv_adapter_loads_rows_and_documents_are_searchable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "people.csv"
            path.write_text("name,age,team\nAlice,31,TraceQL\nBob,24,Logger\n", encoding="utf-8")

            rows = load_csv(path)
            documents = CsvAdapter(path).documents()

        self.assertEqual(rows[0]["name"], "Alice")
        self.assertTrue(match_query("name:Alice age>=30 TraceQL", documents[0]))
        self.assertTrue(match_query("metadata.table:people", documents[0]))

    def test_json_adapter_accepts_list_and_embedded_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            list_path = Path(temp_dir) / "items.json"
            list_path.write_text(json.dumps([{"name": "Access", "kind": "db"}]), encoding="utf-8")
            wrapped_path = Path(temp_dir) / "wrapped.json"
            wrapped_path.write_text(json.dumps({"rows": [{"name": "Excel", "kind": "sheet"}]}), encoding="utf-8")

            list_rows = load_json(list_path)
            wrapped_documents = JsonAdapter(wrapped_path).documents()

        self.assertEqual(list_rows[0]["name"], "Access")
        self.assertTrue(match_query("name:Excel kind:sheet", wrapped_documents[0]))

    def test_pandas_adapter_accepts_dataframe_like_object(self) -> None:
        dataframe = FakeDataFrame([{"name": "GPU", "usage": 88}, {"name": "CPU", "usage": 42}])
        documents = PandasAdapter(dataframe, table="metrics").documents()

        self.assertTrue(match_query("name:GPU usage>=80 metadata.table:metrics", documents[0]))

    def test_row_to_document_keeps_original_fields_at_top_level(self) -> None:
        document = row_to_document({"customer": "Kurokawa", "score": 95}, source="memory", table="scores")

        self.assertTrue(match_query("customer:Kurokawa score>=90 metadata.source:memory", document))


if __name__ == "__main__":
    unittest.main()
