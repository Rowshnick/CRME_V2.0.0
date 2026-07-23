import os
import json
from datetime import datetime


class ExportBundleEngine:
    def __init__(self, base_path):
        self.base_path = base_path
        self.memory_path = os.path.join(base_path, "memory")
        self.export_path = os.path.join(self.memory_path, "exports")

        os.makedirs(self.export_path, exist_ok=True)

    # =========================
    # LOAD HELPERS
    # =========================
    def _load_json(self, path):
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_text(self, path):
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # =========================
    # BUILD PCB
    # =========================
    def build(self):
        dashboard = self._load_json(os.path.join(self.memory_path, "dashboard.json"))
        session_summary = self._load_json(os.path.join(self.memory_path, "session_summary.json"))
        latest_md = self._load_text(os.path.join(self.memory_path, "latest.md"))
        dashboard_md = self._load_text(os.path.join(self.memory_path, "dashboard.md"))

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        bundle_dir = os.path.join(self.export_path, f"PCB_{timestamp}")
        os.makedirs(bundle_dir, exist_ok=True)

        # =========================
        # context.json
        # =========================
        context = {
            "dashboard": dashboard,
            "session_summary": session_summary,
            "generated_at": timestamp,
            "system": "CRME v1.0.2 PCB"
        }

        context_json_path = os.path.join(bundle_dir, "context.json")
        with open(context_json_path, "w", encoding="utf-8") as f:
            json.dump(context, f, indent=2, ensure_ascii=False)

        # =========================
        # context.md
        # =========================
        context_md = f"""
# 🧠 CRME Portable Context Bundle

Generated: {timestamp}

---

# 📊 Dashboard

{dashboard_md}

---

# 📄 Latest Memory Pack

{latest_md}

---

# 🔁 Resume Prompt

You are continuing a CRME project.

Use this bundle as the full memory state.

Do NOT redesign architecture.

Continue from latest session state.

Version: CRME v1.0.2 PCB
"""

        context_md_path = os.path.join(bundle_dir, "context.md")
        with open(context_md_path, "w", encoding="utf-8") as f:
            f.write(context_md)

        # =========================
        # resume_prompt.txt (clean LLM input)
        # =========================
        resume_prompt = """
You are continuing the CRME project.

You are given a Portable Context Bundle (PCB).

Rules:
- Do not redesign architecture
- Continue from latest session state
- Use dashboard as source of truth
- Preserve memory consistency

Task:
Continue CRME execution from this state.
"""

        resume_path = os.path.join(bundle_dir, "resume_prompt.txt")
        with open(resume_path, "w", encoding="utf-8") as f:
            f.write(resume_prompt)

        return {
            "status": "success",
            "bundle_path": bundle_dir,
            "files": {
                "context_json": context_json_path,
                "context_md": context_md_path,
                "resume_prompt": resume_path
            }
        }
