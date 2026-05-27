"""検索対象をQuery EngineのDocumentへ変換するアダプタ群。"""
from __future__ import annotations

from query_engine.adapters.access_adapter import AccessAdapter, access_to_documents, load_access
from query_engine.adapters.browser import BrowserPage, browser_page_to_document
from query_engine.adapters.csv_adapter import CsvAdapter, csv_to_documents, load_csv
from query_engine.adapters.documents import TextDocument, from_text, from_text_file, normalize_text
from query_engine.adapters.extractors import extract_text_file
from query_engine.adapters.json_adapter import JsonAdapter, json_to_documents, load_json
from query_engine.adapters.logs import log_to_document
from query_engine.adapters.pandas_adapter import PandasAdapter, dataframe_to_documents, dataframe_to_records
from query_engine.adapters.tabular import Record, row_to_document, rows_to_documents
from query_engine.adapters.universal_adapter import SORRY_MESSAGE, UniversalAdapter, universal_to_documents
from query_engine.adapters.xml_adapter import XmlAdapter, load_xml, xml_to_documents

__all__: list[str] = [
    "AccessAdapter",
    "BrowserPage",
    "CsvAdapter",
    "JsonAdapter",
    "PandasAdapter",
    "Record",
    "SORRY_MESSAGE",
    "TextDocument",
    "UniversalAdapter",
    "XmlAdapter",
    "access_to_documents",
    "browser_page_to_document",
    "csv_to_documents",
    "dataframe_to_documents",
    "dataframe_to_records",
    "extract_text_file",
    "from_text",
    "from_text_file",
    "json_to_documents",
    "load_access",
    "load_csv",
    "load_json",
    "load_xml",
    "log_to_document",
    "normalize_text",
    "row_to_document",
    "rows_to_documents",
    "universal_to_documents",
    "xml_to_documents",
]
