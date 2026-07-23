import json
import os
from datetime import datetime


class SessionExporter:
    def __init__(self, base_path):
        self.base_path = base_path

    def export_summary(self, index):

        # 🔵 DEDUP BEFORE EXPORT
        def unique(items):
            seen = set()
            out = []
            for x in items:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        summary = {
            "timestamp": str(datetime.now()),
            "goals": unique([o["content"] for o in index.get("objects", []) if o["type"] == "Goal"]),
            "decisions": unique([o["content"] for o in index.get("objects", []) if o["type"] == "Decision"]),
            "open_tasks": unique([o["content"] for o in index.get("objects", []) if o["type"] == "Task"]),
            "latest_session": index["sessions"][-1] if index.get("sessions") else None,
            "graph_stats": {
                "objects": len(index.get("objects", [])),
                "relations": len(index.get("relations", [])),
                "sessions": len(index.get("sessions", []))
            }
        }

        return summary

    def save(self, summary):
        path = os.path.join(self.base_path, "memory", "session_summary.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return path

