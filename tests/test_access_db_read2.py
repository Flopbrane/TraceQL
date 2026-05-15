# -*- coding: utf-8 -*-
"""access DB read test2"""
#########################
# Author: F.Kurokawa
# Description:
# access database read test2
#########################
from typing import Any, Mapping

from query_engine.adapters.access_adapter import AccessAdapter
from query_engine.evaluators.memory import search
from query_engine.models import SearchResult

documents: list[Mapping[str, Any]] = AccessAdapter(
    r"D:\PC\Python\traceql\examples\sample_traceql.accdb",
    table="customers",
).documents()

results: list[SearchResult] = search("東京 amount>=10000", documents)
print(results[0].document["name"])

results2: list[SearchResult] = search("area:東京 product:TraceQL", documents)
print(results2[0].document["name"])
