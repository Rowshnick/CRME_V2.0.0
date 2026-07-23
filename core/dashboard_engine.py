import os
import json
from datetime import datetime


class DashboardEngine:
    def __init__(self, base_path):
        self.base_path = base_path
        self.memory_path = os.path.join(base_path, "memory")
        self.index_path = os.path.join(self.memory_path, "index.json")

        os.makedirs(self.memory_path, exist_ok=True)

    # =========================
    # LOAD INDEX
    # =========================
    def _load_index(self):
        if not os.path.exists(self.index_path):
            return {"objects": [], "relations": [], "sessions": []}

        with open(self.index_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # =========================
    # BUILD DASHBOARD CONTEXT
    # =========================
    def build(self):
        index = self._load_index()

        objects = index.get("objects", [])
        sessions = index.get("sessions", [])

        goals = [o["content"] for o in objects if o["type"] == "Goal"]
        decisions = [o["content"] for o in objects if o["type"] == "Decision"]
        tasks = [o["content"] for o in objects if o["type"] == "Task"]

        latest_session = sessions[-1] if sessions else None

        dashboard = {
            "project_identity": {
                "name": "CRME",
                "version": "v1.0.1 Stable",
                "status": "operational"
            },

            "completed_releases": [
                "v0.1 Memory Extraction",
                "v0.2 Pack System",
                "v0.3 Index Engine",
                "v0.4 Session Engine",
                "v0.5 Graph Layer",
                "v0.6 Semantic Engine",
                "v0.7 Auto Continuity",
                "v0.8 Intelligence Layer",
                "v0.9 Autonomous Mode",
                "v1.0 Export + Stability",
                "v1.0.1 Dashboard Upgrade"
            ],

            "architecture_snapshot": {
                "layers": [
                    "MemoryEngine",
                    "Indexer",
                    "SessionEngine",
                    "SemanticEngine",
                    "ExportEngine",
                    "DashboardEngine"
                ]
            },

            "statistics": {
                "total_objects": len(objects),
                "total_relations": len(index.get("relations", [])),
                "total_sessions": len(sessions),
                "goals": len(goals),
                "decisions": len(decisions),
                "tasks": len(tasks)
            },

            "key_decisions": list(set(decisions)),
            "open_tasks": list(set(tasks)),
            "latest_session": latest_session,

            "research_direction": [
                "Portable Cognitive Memory Systems",
                "Session Continuity",
                "Graph-Based Reasoning",
                "AI Memory OS Architecture"
            ],

            "resume_prompt": (
                "You are continuing CRME v1.0.1. "
                "Use dashboard as authoritative memory. "
                "Do not redesign architecture. "
                "Continue only from open tasks."
            ),

            "generated_at": str(datetime.now())
        }

        return dashboard

    # =========================
    # EXPORT JSON
    # =========================
    def export_json(self, dashboard):
        path = os.path.join(self.memory_path, "dashboard.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(dashboard, f, indent=2, ensure_ascii=False)

        return path

    # =========================
    # EXPORT MARKDOWN (NEW)
    # =========================
    def export_md(self, dashboard):
        path = os.path.join(self.memory_path, "dashboard.md")

        md = []

        md.append("# 🧠 CRME DASHBOARD\n")

        md.append(f"## Project Identity\n- Name: {dashboard['project_identity']['name']}\n- Version: {dashboard['project_identity']['version']}\n- Status: {dashboard['project_identity']['status']}\n")

        md.append("## 📊 Statistics\n")
        for k, v in dashboard["statistics"].items():
            md.append(f"- {k}: {v}\n")

        md.append("\n## 🎯 Key Decisions\n")
        for d in dashboard["key_decisions"]:
            md.append(f"- {d}\n")

        md.append("\n## 📌 Open Tasks\n")
        for t in dashboard["open_tasks"]:
            md.append(f"- {t}\n")

        md.append("\n## 🧭 Research Direction\n")
        for r in dashboard["research_direction"]:
            md.append(f"- {r}\n")

        md.append("\n## 🔁 Resume Prompt\n")
        md.append(dashboard["resume_prompt"] + "\n")

        md.append("\n## 🕒 Latest Session\n")
        md.append(json.dumps(dashboard["latest_session"], indent=2, ensure_ascii=False))

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))

        return path

