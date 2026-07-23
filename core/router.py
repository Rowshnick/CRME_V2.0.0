from core.pipeline import run_pipeline
from core.query_engine import QueryEngine
from core.export_bundle import ExportBundleEngine
from core.dashboard_engine import DashboardEngine
from core.session_engine import SessionEngine
from core.indexer import Indexer


class CommandRouter:
    def __init__(self):
        self.base_path = "."
        self.qe = QueryEngine(".")
        self.indexer = Indexer(".")
        self.session = SessionEngine(".")
        self.dashboard = DashboardEngine(".")
        self.exporter = ExportBundleEngine(".")

    # =========================
    # ROUTE COMMANDS
    # =========================
    def route(self, command, args):

        if command == "status":
            return self._status()

        if command == "continue":
            return self._continue()

        if command == "query":
            return self._query(args)

        if command == "export":
            return self._export()

        if command == "resume":
            return self._resume()

        return {"error": "unknown command"}

    # =========================
    # COMMANDS
    # =========================
    def _status(self):
        dash = self.dashboard.build()
        return {
            "project": "CRME",
            "version": "v1.0.3 CLI",
            "stats": dash["statistics"]
        }

    def _continue(self):
        from core.pipeline import run_pipeline
        return run_pipeline()

    def _query(self, args):
        q = " ".join(args)
        return self.qe.query(q)

    def _export(self):
        return self.exporter.build()

    def _resume(self):
        return {
            "status": "ready",
            "message": "Use dashboard.md as memory state input"
        }

