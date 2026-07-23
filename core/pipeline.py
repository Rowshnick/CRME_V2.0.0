import os
import sys
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.memory_engine import MemoryEngine
from core.pack_generator import MemoryPackGenerator
from core.object_model import ResearchObject
from core.indexer import Indexer
from core.session_engine import SessionEngine
from core.export_engine import ExportEngine
from core.dashboard_engine import DashboardEngine
from core.export_bundle import ExportBundleEngine


# ==========================================================
# CORE PIPELINE FUNCTION (CLI COMPATIBLE)
# ==========================================================

def run_pipeline():
    chat_file = os.path.join(PROJECT_ROOT, "input_chat.txt")

    with open(chat_file, "r", encoding="utf-8") as f:
        text = f.read()

    # ==============================
    # 1. MEMORY EXTRACTION
    # ==============================
    engine = MemoryEngine(text)
    result = engine.extract()

    print("\n🧠 EXTRACTION RESULT\n")
    print(result)

    # ==============================
    # 2. INDEX BUILDING
    # ==============================
    indexer = Indexer(PROJECT_ROOT)
    objects = []

    # Goals
    for g in result.get("goals", []):
        obj = ResearchObject("Goal", g)
        indexer.add_object(obj)
        objects.append(obj)

    # Decisions
    for d in result.get("decisions", []):
        obj = ResearchObject("Decision", d)
        indexer.add_object(obj)
        objects.append(obj)

    # Tasks
    for n in result.get("next_steps", []):
        obj = ResearchObject("Task", n)
        indexer.add_object(obj)
        objects.append(obj)

    # ==============================
    # 3. MEMORY PACK GENERATION
    # ==============================
    generator = MemoryPackGenerator(result)
    md = generator.build_markdown()
    generator.save(md, PROJECT_ROOT)

    latest_path = os.path.join(PROJECT_ROOT, "memory", "latest.md")

    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(md)

    # ==============================
    # 4. SESSION ENGINE
    # ==============================
    session_engine = SessionEngine(PROJECT_ROOT)
    session_id, session_file = session_engine.create_session_snapshot(
        objects,
        result
    )

    print("\n🧭 SESSION CREATED:")
    print(session_id)
    print(session_file)

    # ==============================
    # 5. GRAPH LINKS
    # ==============================
    for i in range(len(objects) - 1):
        indexer.add_relation(
            objects[i].id,
            objects[i + 1].id
        )

    print("\n🔗 GRAPH UPDATED")

    # ==============================
    # 6. EXPORT ENGINE
    # ==============================
    export_engine = ExportEngine(PROJECT_ROOT)
    export_result = export_engine.export(indexer.index)

    print("\n📦 EXPORT CREATED:")
    print(export_result)

    # ==============================
    # 7. DASHBOARD LAYER (v1.0.1)
    # ==============================
    dashboard_engine = DashboardEngine(PROJECT_ROOT)

    dashboard = dashboard_engine.build()

    dash_json = dashboard_engine.export_json(dashboard)
    dash_md = dashboard_engine.export_md(dashboard)

    print("\n📊 DASHBOARD CREATED:")
    print("JSON:", dash_json)
    print("MD:", dash_md)

    # ==============================
    # 8. PCB LAYER (v1.0.2)
    # ==============================
    pcb_engine = ExportBundleEngine(PROJECT_ROOT)

    pcb_result = pcb_engine.build()

    print("\n📦 PCB CREATED:")
    print(pcb_result["bundle_path"])

    print("\n✔ CRME v1.0.3 PIPELINE COMPLETE")

    return {
        "status": "success",
        "session_id": session_id,
        "export": export_result,
        "dashboard": dash_json,
        "pcb": pcb_result["bundle_path"]
    }


# ==========================================================
# CLI ENTRY SUPPORT (optional direct run)
# ==========================================================

if __name__ == "__main__":
    run_pipeline()

