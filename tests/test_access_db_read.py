# -*- coding: utf-8 -*-
"""access-test.py"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from typing import Any, Mapping

from query_engine.adapters.access_adapter import AccessAdapter
from query_engine.evaluators.memory import search
from query_engine.models import SearchResult

path = r"D:\PC\Python\traceql\examples\sample_traceql.accdb"

documents: list[Mapping[str, Any]] = AccessAdapter(path, table="customers").documents()
results: list[SearchResult] = search("area:東京 amount>=10000", documents)

print(results[0].document)
