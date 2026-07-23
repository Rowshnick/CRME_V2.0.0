import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.query_engine import QueryEngine

qe = QueryEngine(PROJECT_ROOT)

print("\n🧠 ALL DECISIONS:\n")
print(qe.search_by_type("Decision"))

print("\n🔍 KEYWORD SEARCH (memory):\n")
print(qe.search_by_keyword("memory"))

print("\n🧭 LATEST SESSION:\n")
print(qe.get_latest_session())

print("\n⚡ SEMANTIC QUERY:\n")
print(qe.query("show decisions about memory"))


