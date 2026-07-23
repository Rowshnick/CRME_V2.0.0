import os
import json
import zipfile
from datetime import datetime, timezone


class ContextExporter:
    """
    CRME Context Export Layer v2.0

    Responsibilities
    ----------------
    - LLM-independent context transfer
    - Research snapshot export
    - Project brief generation
    - Research package generation
    - Export manifest creation
    - Session continuity export
    - Change history preservation
    """

    VERSION = "2.0.0"

    def __init__(
        self,
        project_engine,
        session_engine,
        graph_engine
    ):
        self.project_engine = project_engine
        self.session_engine = session_engine
        self.graph_engine = graph_engine

        self.export_root = "exports"

        self.snapshot_dir = os.path.join(
            self.export_root,
            "snapshots"
        )

        self.brief_dir = os.path.join(
            self.export_root,
            "briefs"
        )

        self.package_dir = os.path.join(
            self.export_root,
            "packages"
        )

        self._prepare_directories()

    # =====================================================
    # TIME
    # =====================================================

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    # =====================================================
    # DIRECTORY INITIALIZATION
    # =====================================================

    def _prepare_directories(self):

        for path in [
            self.snapshot_dir,
            self.brief_dir,
            self.package_dir
        ]:

            os.makedirs(
                path,
                exist_ok=True
            )

    # =====================================================
    # SESSION EXPORT
    # =====================================================

    def _export_sessions(self):

        sessions = []

        path = self.session_engine.session_dir

        if not os.path.exists(path):

            return sessions

        for file in sorted(os.listdir(path)):

            if not file.endswith(".json"):

                continue

            full_path = os.path.join(
                path,
                file
            )

            try:

                with open(
                    full_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    sessions.append(
                        json.load(f)
                    )

            except (
                json.JSONDecodeError,
                OSError
            ):

                continue

        return sessions

    # =====================================================
    # CHANGE HISTORY EXPORT
    # =====================================================

    def _export_change_history(self):

        history = []

        sessions = self._export_sessions()

        for session in sessions:

            session_id = session.get(
                "session_id"
            )

            if not session_id:

                continue

            try:

                changes = (
                    self.session_engine
                    .get_session_changes(
                        session_id
                    )
                )

                history.extend(
                    changes or []
                )

            except Exception:

                continue

        return history

    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    def build(self):

        project = (
            self.project_engine.to_dict()
        )

        summary = (
            self.project_engine.summary()
        )

        graph = (
            self.graph_engine.export()
        )

        sessions = (
            self._export_sessions()
        )

        return {

            "metadata": {

                "system": "CRME",

                "export_layer_version":
                    self.VERSION,

                "created_at":
                    self._now(),

                "format":
                    "LLM_INDEPENDENT_RESEARCH_CONTEXT"

            },

            "project": project,

            "summary": summary,

            "research": {

                "ledger":
                    project.get(
                        "research_ledger",
                        []
                    ),

                "decisions":
                    project.get(
                        "decision_log",
                        []
                    ),

                "ideas":
                    project.get(
                        "idea_inbox",
                        []
                    ),

                "provenance":
                    project.get(
                        "provenance_log",
                        []
                    )

            },

            "knowledge_graph": graph,

            "sessions": sessions,

            "change_history":
                self._export_change_history(),

            "transfer_info": {

                "current_stage":
                    "Core Integration Completed",

                "next_stage":
                    "Semantic Query Engine",

                "purpose":
                    "Transfer CRME research state between independent LLM systems",

                "continuity_supported":
                    True,

                "reproducibility_supported":
                    True

            }

        }

    # =====================================================
    # SAVE SNAPSHOT
    # =====================================================

    def save_snapshot(
        self,
        filename="CRME_Context_Snapshot_v2.0.json"
    ):

        path = os.path.join(
            self.snapshot_dir,
            filename
        )

        context = self.build()

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                context,
                f,
                indent=2,
                ensure_ascii=False
            )

        self.save_manifest()

        return path

    # =====================================================
    # SAVE PROJECT BRIEF
    # =====================================================

    def save_brief(
        self,
        filename="CRME_PROJECT_BRIEF_v2.0.md"
    ):

        path = os.path.join(
            self.brief_dir,
            filename
        )

        summary = (
            self.project_engine.summary()
        )

        project = (
            self.project_engine.to_dict()
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "# CRME PROJECT BRIEF\n\n"
            )

            f.write(
                "## Project\n\n"
            )

            f.write(
                f"- Name: "
                f"{summary.get('project')}\n"
            )

            f.write(
                f"- Project ID: "
                f"{summary.get('project_id')}\n"
            )

            f.write(
                f"- Status: "
                f"{summary.get('status')}\n"
            )

            f.write(
                f"- Phase: "
                f"{summary.get('phase')}\n"
            )

            f.write(
                f"- Progress: "
                f"{summary.get('progress')}%\n\n"
            )

            f.write(
                "## Research Metrics\n\n"
            )

            f.write(
                f"- Sessions: "
                f"{summary.get('sessions')}\n"
            )

            f.write(
                f"- Decisions: "
                f"{summary.get('decisions')}\n"
            )

            f.write(
                f"- Ideas: "
                f"{summary.get('ideas')}\n"
            )

            f.write(
                f"- Artifacts: "
                f"{summary.get('artifacts')}\n"
            )

            f.write(
                f"- Knowledge Nodes: "
                f"{summary.get('knowledge_nodes')}\n"
            )

            f.write(
                f"- Knowledge Relations: "
                f"{summary.get('knowledge_relations', 0)}\n"
            )

            f.write(
                f"- Memories: "
                f"{summary.get('memories', 0)}\n\n"
            )

            f.write(
                "## Research Decisions\n\n"
            )

            for decision in project.get(
                "decision_log",
                []
            ):

                f.write(
                    f"- {decision}\n"
                )

            f.write(
                "\n## Research Ledger\n\n"
            )

            for entry in project.get(
                "research_ledger",
                []
            ):

                f.write(
                    f"- {entry}\n"
                )

            f.write(
                "\n## Idea Inbox\n\n"
            )

            for idea in project.get(
                "idea_inbox",
                []
            ):

                f.write(
                    f"- {idea}\n"
                )

            f.write(
                "\n## Provenance\n\n"
            )

            for item in project.get(
                "provenance_log",
                []
            ):

                f.write(
                    f"- {item}\n"
                )

            f.write(
                "\n## Next Stage\n\n"
                "Semantic Query Engine\n\n"
            )

            f.write(
                "## Transfer\n\n"
                "This brief is generated by CRME "
                "for LLM-independent research context transfer.\n"
            )

        self.save_manifest()

        return path

    # =====================================================
    # SAVE RESEARCH PACKAGE
    # =====================================================

    def save_package(
        self,
        filename="CRME_RESEARCH_PACKAGE_v2.0.zip"
    ):

        snapshot_path = self.save_snapshot()

        brief_path = self.save_brief()

        manifest_path = self.save_manifest()

        package_path = os.path.join(
            self.package_dir,
            filename
        )

        with zipfile.ZipFile(
            package_path,
            "w",
            compression=zipfile.ZIP_DEFLATED
        ) as archive:

            archive.write(
                snapshot_path,
                arcname=os.path.basename(
                    snapshot_path
                )
            )

            archive.write(
                brief_path,
                arcname=os.path.basename(
                    brief_path
                )
            )

            archive.write(
                manifest_path,
                arcname=os.path.basename(
                    manifest_path
                )
            )

        return package_path

    # =====================================================
    # EXPORT MANIFEST
    # =====================================================

    def save_manifest(self):

        project = (
            self.project_engine.to_dict()
        )

        graph = (
            self.graph_engine.export()
        )

        manifest = {

            "system":
                "CRME",

            "version":
                self.VERSION,

            "created_at":
                self._now(),

            "project_id":
                project.get(
                    "project_id"
                ),

            "project":
                project.get(
                    "title"
                ),

            "exports": {

                "snapshot":
                    True,

                "brief":
                    True,

                "package":
                    True,

                "knowledge_graph":
                    True,

                "change_history":
                    True

            },

            "metrics": {

                "knowledge_nodes":
                    len(
                        graph.get(
                            "objects",
                            []
                        )
                    ),

                "knowledge_relations":
                    len(
                        graph.get(
                            "relations",
                            []
                        )
                    )

            },

            "ready_for_llm_transfer":
                True

        }

        path = os.path.join(
            self.export_root,
            "CRME_EXPORT_MANIFEST.json"
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                manifest,
                f,
                indent=2,
                ensure_ascii=False
            )

        return path

