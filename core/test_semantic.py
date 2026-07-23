import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.query_engine import QueryEngine

qe = QueryEngine(PROJECT_ROOT)

print("\n🧠 SEMANTIC SEARCH:\n")
print(qe.semantic_search("memory system architecture"))

print("\n📦 CLUSTERS:\n")
print(qe.cluster())

