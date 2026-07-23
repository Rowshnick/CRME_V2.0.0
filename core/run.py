import sys
import os

# اضافه کردن root پروژه به مسیر
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory_engine import MemoryEngine

sample_text = """
Goal: build structured memory system
Decision: store memory locally in Termux
Next: automate pipeline
"""

engine = MemoryEngine(sample_text)
result = engine.extract()

print("=== MEMORY OUTPUT ===")
print(result)


