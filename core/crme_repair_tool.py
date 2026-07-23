import os
import json
from datetime import datetime


class CRMERepairTool:
    """
    🛠️ CRME Auto-Healer System
    --------------------------
    مسئول:
    - تشخیص خرابی ساختار هسته CRME
    - تعمیر فایل‌های core
    - بازسازی API های گمشده
    - بررسی integrity سیستم
    """

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.core_path = os.path.join(base_path, "core")

    # =========================================================
    # 🔍 HEALTH CHECK
    # =========================================================

    def run_health_check(self):
        """
        بررسی وضعیت کل سیستم CRME
        """

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "UNKNOWN",
            "issues": [],
            "ok": []
        }

        required_files = {
            "session_engine.py": "SessionEngine",
            "project_engine.py": "ResearchProject",
            "crme_kernel.py": "CRMEKernel"
        }

        for file, expected_class in required_files.items():
            path = os.path.join(self.core_path, file)

            if not os.path.exists(path):
                report["issues"].append(f"MISSING FILE: {file}")
                continue

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            if f"class {expected_class}" not in content:
                report["issues"].append(
                    f"INVALID CLASS in {file} (expected {expected_class})"
                )
            else:
                report["ok"].append(file)

        report["status"] = "HEALTHY" if not report["issues"] else "BROKEN"

        return report

    # =========================================================
    # 🧠 AUTO FIX ENGINE
    # =========================================================

    def auto_fix(self):
        """
        تلاش برای تعمیر خودکار فایل‌های خراب
        """

        report = self.run_health_check()

        fixes = []

        for issue in report["issues"]:

            # -------------------------------------------------
            # FIX: missing crme_kernel.py
            # -------------------------------------------------
            if "crme_kernel.py" in issue and "MISSING" in issue:
                self._create_kernel()
                fixes.append("Created missing crme_kernel.py")

            # -------------------------------------------------
            # FIX: session_engine broken
            # -------------------------------------------------
            if "session_engine.py" in issue:
                self._restore_session_engine()
                fixes.append("Restored session_engine.py")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "fixes": fixes,
            "status_after": self.run_health_check()
        }

    # =========================================================
    # 🔧 RESTORE MODULES
    # =========================================================

    def _restore_session_engine(self):
        path = os.path.join(self.core_path, "session_engine.py")

        code = '''
import os
import json
from datetime import datetime


class SessionEngine:
    def __init__(self, base_path):
        self.base_path = base_path
        self.session_dir = os.path.join(base_path, "memory", "sessions")
        os.makedirs(self.session_dir, exist_ok=True)

    def create_session(self, project_id=None, metadata=None):
        session_id = f"S-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        session = {
            "session_id": session_id,
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "state": {
                "messages": [],
                "decisions": [],
                "goals": []
            },
            "version": 1
        }

        path = os.path.join(self.session_dir, f"{session_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2)

        return session_id
'''

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

    # =========================================================
    # 🧠 CREATE KERNEL IF MISSING
    # =========================================================

    def _create_kernel(self):
        path = os.path.join(self.core_path, "crme_kernel.py")

        code = '''
class CRMEKernel:
    def __init__(self, session_engine, project_engine):
        self.session_engine = session_engine
        self.project_engine = project_engine

    def start_session(self, project_id=None, metadata=None):
        return self.session_engine.create_session(project_id, metadata)

    def update(self, session_id, update):
        self.session_engine.update_session(session_id, update)
        session = self.session_engine.get_snapshot(session_id)

        self.project_engine.handle_session_event(
            "session_updated",
            {"session_id": session_id, "state": session["state"]}
        )

    def get_latest_state(self, session_id=None):
        session = None
        if session_id:
            session = self.session_engine.get_snapshot(session_id)

        return {
            "session": session,
            "project": self.project_engine.export_project()
        }
'''

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

