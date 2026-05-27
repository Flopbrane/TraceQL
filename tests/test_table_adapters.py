import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from query_engine.adapters.csv_adapter import CsvAdapter, load_csv
from query_engine.adapters.json_adapter import JsonAdapter, load_json
from query_engine.adapters.pandas_adapter import PandasAdapter
from query_engine.adapters.tabular import row_to_document
from query_engine.adapters.universal_adapter import SORRY_MESSAGE, UniversalAdapter
from query_engine.adapters.xml_adapter import XmlAdapter, load_xml
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

    def test_xml_adapter_loads_elements_and_attributes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "books.xml"
            path.write_text(
                """
                <library>
                  <book id="b1" category="python">
                    <title>TraceQL Guide</title>
                    <author>Kurokawa</author>
                  </book>
                </library>
                """,
                encoding="utf-8",
            )

            rows = load_xml(path)
            documents = XmlAdapter(path).documents()

        self.assertEqual(rows[1]["tag"], "book")
        self.assertEqual(rows[1]["attributes"]["id"], "b1")
        self.assertEqual(rows[2]["path"], "library/book[1]/title[1]")
        self.assertTrue(match_query("tag:book attributes.id:b1 category:python", documents[1]))
        self.assertTrue(match_query("path:book text:TraceQL", documents[2]))

    def test_universal_adapter_infers_broken_json_like_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "broken.data"
            path.write_text(
                '{level: ERROR, message: "Disk full", file_path: D:\\logs\\app.py}\n'
                "{level: INFO, message: recovered}\n",
                encoding="utf-8",
            )

            documents = UniversalAdapter(path).documents()

        self.assertTrue(match_query("level:ERROR message:Disk file_path:app.py", documents[0]))
        self.assertEqual(documents[0]["metadata"]["adapter"], "universal")
        self.assertEqual(documents[0]["metadata"]["strategy"], "inferred_records")

    def test_universal_adapter_returns_unrecognized_document_for_empty_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "empty.bin"
            path.write_text("", encoding="utf-8")

            documents = UniversalAdapter(path).documents()

        self.assertEqual(documents[0]["title"], SORRY_MESSAGE)
        self.assertEqual(documents[0]["metadata"]["strategy"], "unrecognized")

    def test_universal_adapter_detects_encoding_and_partial_ast_signals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "legacy.txt"
            path.write_bytes("message=警告 eval(payload)".encode("cp932"))

            documents = UniversalAdapter(path).documents()

        self.assertTrue(match_query("message:警告", documents[0]))
        self.assertIn(documents[0]["metadata"]["encoding"], {"cp932", "shift_jis"})
        self.assertIn("eval_call", documents[0]["metadata"]["partial_ast_signals"])

    def test_universal_adapter_detects_binary_magic_and_entropy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.exe"
            path.write_bytes(b"MZ" + bytes(range(256)) * 4)

            documents = UniversalAdapter(path).documents()

        self.assertIn("mz_executable", documents[0]["metadata"]["binary_signals"])
        self.assertGreater(documents[0]["metadata"]["entropy_score"], 0)

    def test_pandas_adapter_accepts_dataframe_like_object(self) -> None:
        dataframe = FakeDataFrame([{"name": "GPU", "usage": 88}, {"name": "CPU", "usage": 42}])
        documents = PandasAdapter(dataframe, table="metrics").documents()

        self.assertTrue(match_query("name:GPU usage>=80 metadata.table:metrics", documents[0]))

    def test_row_to_document_keeps_original_fields_at_top_level(self) -> None:
        document = row_to_document({"customer": "Kurokawa", "score": 95}, source="memory", table="scores")

        self.assertTrue(match_query("customer:Kurokawa score>=90 metadata.source:memory", document))


if __name__ == "__main__":
    unittest.main()
