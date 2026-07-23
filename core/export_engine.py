import os
import json
from datetime import datetime


class ExportEngine:
    def __init__(self, base_path):
        self.base_path = base_path
        self.memory_path = os.path.join(base_path, "memory")

        self.export_dir = os.path.join(self.memory_path, "exports")
        os.makedirs(self.export_dir, exist_ok=True)

    # =========================
    # MAIN EXPORT FUNCTION
    # =========================
    def export(self, index):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        context = self._build_context(index)

        md_path = self._save_md(context, timestamp)
        json_path = self._save_json(context, timestamp)

        return {
            "status": "success",
            "md": md_path,
            "json": json_path
        }

    # =========================
    # CONTEXT BUILDER
    # =========================
    def _build_context(self, index):

        goals = [o["content"] for o in index.get("objects", []) if o["type"] == "Goal"]
        decisions = [o["content"] for o in index.get("objects", []) if o["type"] == "Decision"]
        tasks = [o["content"] for o in index.get("objects", []) if o["type"] == "Task"]

        return {
            "project_identity": {
                "name": "CRME",
                "version": "v1.0 Stable",
                "status": "stable"
            },
            "completed_releases": [
                "v0.1 Memory Extraction",
                "v0.2 Memory Packs",
                "v0.3 Indexing",
                "v0.4 Session Engine",
                "v0.5 Graph Layer",
                "v0.6 Semantic Search",
                "v0.7 Auto Continuity",
                "v0.8 Memory Intelligence",
                "v0.9 Autonomous Mode",
                "v0.9.1 Loop",
                "v0.9.2 Export Layer"
            ],
            "architecture_snapshot": {
                "layers": [
                    "QueryEngine",
                    "SemanticEngine",
                    "SessionEngine",
                    "Indexer",
                    "MemoryEngine"
                ]
            },
            "key_decisions": list(set(decisions)),
            "open_tasks": list(set(tasks)),
            "research_direction": [
                "Portable Memory Systems",
                "Session Continuity",
                "Knowledge Compression"
            ],
            "resume_prompt": (
                "This is CRME v1.0 Stable context. "
                "Continue from Open Tasks without redesigning existing system."
            )
        }

    # =========================
    # MARKDOWN EXPORT
    # =========================
    def _save_md(self, context, timestamp):
        path = os.path.join(self.export_dir, f"CRME_Context_{timestamp}.md")

        md = "# CRME CONTEXT EXPORT\n\n"
        md += f"Version: {context['project_identity']['version']}\n\n"

        md += "## Key Decisions\n"
        for d in context["key_decisions"]:
            md += f"- {d}\n"

        md += "\n## Open Tasks\n"
        for t in context["open_tasks"]:
            md += f"- {t}\n"

        md += "\n## Resume Prompt\n"
        md += context["resume_prompt"] + "\n"

        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

        return path

    # =========================
    # JSON EXPORT
    # =========================
    def _save_json(self, context, timestamp):
        path = os.path.join(self.export_dir, f"CRME_Context_{timestamp}.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(context, f, indent=2, ensure_ascii=False)

        return path

