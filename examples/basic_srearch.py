# -*- coding: utf-8 -*-

#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from query_engine.ast import QueryNode
from query_engine.models import AggregateQuery, FieldFilter, IgnoreRule, SearchableLog, SortSpec
from query_engine.tokennizer import parse_query

query = parse_query(
    "level:ERROR cpu"
)