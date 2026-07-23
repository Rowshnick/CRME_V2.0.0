import json
import os
from datetime import datetime, timezone
from copy import deepcopy


class ResearchProject:
    """
    CRME Research Project Engine
    ============================

    Research project lifecycle and control layer.

    Responsibilities
    ----------------
    - Project lifecycle
    - Session management
    - Research Ledger
    - Decision Log
    - Idea Inbox
    - Research Provenance
    - Milestones
    - Publications
    - Dependencies
    - Dependency Graph
    - Knowledge Graph synchronization
    - Progress tracking
    - Version tracking
    - Gantt-like timeline
    - Persistent project state

    Design Principle
    ----------------
    This engine is an orchestration and project-control layer.

    It does not replace:
        SessionEngine
        MemoryEngine
        GraphEngine
        ChangeTrackingEngine

    It coordinates their project-level consequences.
    """

    VERSION = "2.0.0"

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(
        self,
        project_id,
        title,
        description="",
        paper_target="Q1",
        repository="",
        tags=None,
        project_path=None,
    ):

        self.project_id = project_id
        self.title = title
        self.description = description
        self.paper_target = paper_target
        self.repository = repository

        self.status = "Active"
        self.current_phase = "Initialization"

        now = self._now()

        self.created_at = now
        self.updated_at = now

        self.progress = 0

        # -----------------------------------------------------
        # CORE PROJECT COLLECTIONS
        # -----------------------------------------------------

        self.sessions = []
        self.milestones = []
        self.publications = []

        self.research_ledger = []
        self.decision_log = []
        self.idea_inbox = []
        self.provenance_log = []

        # -----------------------------------------------------
        # PROJECT CONTROL
        # -----------------------------------------------------

        self.dependencies = []

        self.dependency_graph = {
            "nodes": [],
            "edges": [],
        }

        self.version_history = []

        self.timeline = []

        # -----------------------------------------------------
        # KNOWLEDGE GRAPH METRICS
        # -----------------------------------------------------

        self.knowledge_metrics = {
            "nodes": 0,
            "relations": 0,
            "memories": 0,
        }

        # -----------------------------------------------------
        # PROJECT METADATA
        # -----------------------------------------------------

        self.tags = tags or []

        self.project_path = project_path

        self.engine_version = self.VERSION

        self._record_version(
            event="project_created",
            description="Research project initialized",
        )

    # =========================================================
    # TIME
    # =========================================================

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()

    # =========================================================
    # PROJECT LIFECYCLE
    # =========================================================

    def update_status(self, status, reason=""):
        """
        Update project status.

        Example:
            Active
            Paused
            Stable
            Completed
            Archived
        """

        previous_status = self.status

        self.status = status

        self._record_ledger(
            event="status_changed",
            details={
                "before": previous_status,
                "after": status,
                "reason": reason,
            },
        )

        self._touch()

        return self.status

    def update_phase(self, phase, reason=""):
        """
        Move project to a new research phase.
        """

        previous_phase = self.current_phase

        self.current_phase = phase

        self._record_ledger(
            event="phase_changed",
            details={
                "before": previous_phase,
                "after": phase,
                "reason": reason,
            },
        )

        self._touch()

        return self.current_phase

    def update_progress(self, progress):
        """
        Explicit progress update.

        Value is clamped to [0, 100].
        """

        try:
            progress = float(progress)
        except (TypeError, ValueError):
            raise ValueError("Progress must be numeric.")

        self.progress = max(0, min(100, progress))

        self._touch()

        return self.progress

    # =========================================================
    # SESSION EVENT API
    # =========================================================

    def handle_session_event(
        self,
        event_type,
        payload,
    ):
        """
        Handle events received from SessionEngine / CRMEKernel.

        Supported events:
            session_created
            session_updated
            session_finalized
            session_bound
        """

        payload = payload or {}

        timestamp = self._now()

        session_id = payload.get("session_id")

        state = payload.get(
            "state",
            {},
        )

        if event_type == "session_created":

            if session_id and session_id not in self.sessions:

                self.sessions.append(
                    session_id
                )

            self._record_ledger(
                event="session_created",
                session_id=session_id,
                details=payload,
            )

        elif event_type == "session_updated":

            if session_id and session_id not in self.sessions:

                self.sessions.append(
                    session_id
                )

            self._ingest_session_state(
                session_id=session_id,
                state=state,
            )

            self._record_ledger(
                event="session_updated",
                session_id=session_id,
                details={
                    "state_keys": list(
                        state.keys()
                    )
                },
            )

        elif event_type == "session_finalized":

            self._record_ledger(
                event="session_finalized",
                session_id=session_id,
                details=payload,
            )

        elif event_type == "session_bound":

            if session_id and session_id not in self.sessions:

                self.sessions.append(
                    session_id
                )

            self._record_ledger(
                event="session_bound",
                session_id=session_id,
                details=payload,
            )

        else:

            self._record_ledger(
                event=event_type,
                session_id=session_id,
                details=payload,
            )

        self.updated_at = timestamp

        self._auto_update_progress()

        return {
            "success": True,
            "event": event_type,
            "session_id": session_id,
            "project_id": self.project_id,
        }

    # =========================================================
    # SESSION STATE INGESTION
    # =========================================================

    def _ingest_session_state(
        self,
        session_id,
        state,
    ):

        state = state or {}

        # -----------------------------------------------------
        # DECISIONS
        # -----------------------------------------------------

        for decision in state.get(
            "decisions",
            [],
        ):

            self.add_decision(
                decision=decision,
                session_id=session_id,
                source="session",
            )

        # -----------------------------------------------------
        # GOALS
        # -----------------------------------------------------

        for goal in state.get(
            "goals",
            [],
        ):

            self.add_idea(
                idea=goal,
                session_id=session_id,
                source="session",
            )

        # -----------------------------------------------------
        # ARTIFACTS
        # -----------------------------------------------------

        for artifact in state.get(
            "artifacts",
            [],
        ):

            self.add_provenance(
                artifact=artifact,
                session_id=session_id,
                source="session",
            )

        # -----------------------------------------------------
        # NOTES
        # -----------------------------------------------------

        for note in state.get(
            "notes",
            [],
        ):

            self._record_ledger(
                event="session_note",
                session_id=session_id,
                details={
                    "note": note,
                },
            )

    # =========================================================
    # DECISION LOG
    # =========================================================

    def add_decision(
        self,
        decision,
        session_id=None,
        source="manual",
        decision_id=None,
    ):

        if not decision:
            return None

        # Prevent exact duplicate decisions
        for item in self.decision_log:

            if (
                item.get("decision") == decision
                and item.get("session_id") == session_id
            ):

                return item

        if decision_id is None:

            decision_id = (
                f"DEC-"
                f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
            )

        item = {
            "decision_id": decision_id,
            "decision": decision,
            "session_id": session_id,
            "source": source,
            "timestamp": self._now(),
        }

        self.decision_log.append(
            item
        )

        self._touch()

        return item

    # =========================================================
    # IDEA INBOX
    # =========================================================

    def add_idea(
        self,
        idea,
        session_id=None,
        source="manual",
        status="open",
    ):

        if not idea:
            return None

        for item in self.idea_inbox:

            if (
                item.get("idea") == idea
                and item.get("session_id") == session_id
            ):

                return item

        item = {
            "idea": idea,
            "session_id": session_id,
            "source": source,
            "status": status,
            "timestamp": self._now(),
        }

        self.idea_inbox.append(
            item
        )

        self._touch()

        return item

    def update_idea_status(
        self,
        idea,
        status,
    ):

        updated = []

        for item in self.idea_inbox:

            if item.get("idea") == idea:

                item["status"] = status
                item["updated_at"] = self._now()

                updated.append(
                    item
                )

        self._touch()

        return updated

    # =========================================================
    # RESEARCH PROVENANCE
    # =========================================================

    def add_provenance(
        self,
        artifact,
        session_id=None,
        source="manual",
        metadata=None,
    ):

        if not artifact:
            return None

        item = {
            "artifact": artifact,
            "session_id": session_id,
            "source": source,
            "metadata": metadata or {},
            "timestamp": self._now(),
        }

        self.provenance_log.append(
            item
        )

        self._touch()

        return item

    # =========================================================
    # RESEARCH LEDGER
    # =========================================================

    def add_ledger_entry(
        self,
        event,
        details=None,
        session_id=None,
    ):

        return self._record_ledger(
            event=event,
            session_id=session_id,
            details=details or {},
        )

    def _record_ledger(
        self,
        event,
        session_id=None,
        details=None,
    ):

        entry = {
            "event": event,
            "project_id": self.project_id,
            "session_id": session_id,
            "timestamp": self._now(),
            "details": deepcopy(
                details or {}
            ),
        }

        self.research_ledger.append(
            entry
        )

        self._touch()

        return entry

    # =========================================================
    # MILESTONES
    # =========================================================

    def add_milestone(
        self,
        milestone_id,
        title,
        description="",
        status="pending",
        due_date=None,
        dependencies=None,
    ):

        milestone = {
            "milestone_id": milestone_id,
            "title": title,
            "description": description,
            "status": status,
            "due_date": due_date,
            "dependencies": dependencies or [],
            "created_at": self._now(),
            "updated_at": self._now(),
        }

        self.milestones.append(
            milestone
        )

        self._touch()

        return milestone

    def update_milestone(
        self,
        milestone_id,
        **updates,
    ):

        for milestone in self.milestones:

            if milestone.get(
                "milestone_id"
            ) == milestone_id:

                milestone.update(
                    updates
                )

                milestone["updated_at"] = self._now()

                self._touch()

                return milestone

        return None

    def complete_milestone(
        self,
        milestone_id,
    ):

        return self.update_milestone(
            milestone_id,
            status="completed",
            completed_at=self._now(),
        )

    # =========================================================
    # PUBLICATIONS
    # =========================================================

    def add_publication(
        self,
        title,
        venue="",
        status="planned",
        doi="",
        url="",
    ):

        publication = {
            "title": title,
            "venue": venue,
            "status": status,
            "doi": doi,
            "url": url,
            "created_at": self._now(),
        }

        self.publications.append(
            publication
        )

        self._touch()

        return publication

    # =========================================================
    # DEPENDENCIES
    # =========================================================

    def add_dependency(
        self,
        source,
        target,
        dependency_type="requires",
    ):

        dependency = {
            "source": source,
            "target": target,
            "type": dependency_type,
            "timestamp": self._now(),
        }

        if dependency not in self.dependencies:

            self.dependencies.append(
                dependency
            )

        self._rebuild_dependency_graph()

        self._touch()

        return dependency

    def remove_dependency(
        self,
        source,
        target,
    ):

        self.dependencies = [

            dependency

            for dependency in self.dependencies

            if not (

                dependency.get(
                    "source"
                ) == source

                and dependency.get(
                    "target"
                ) == target

            )

        ]

        self._rebuild_dependency_graph()

        self._touch()

        return True

    def _rebuild_dependency_graph(
        self,
    ):

        nodes = set()
        edges = []

        for dependency in self.dependencies:

            source = dependency.get(
                "source"
            )

            target = dependency.get(
                "target"
            )

            if source:
                nodes.add(source)

            if target:
                nodes.add(target)

            edges.append(
                deepcopy(
                    dependency
                )
            )

        self.dependency_graph = {
            "nodes": sorted(
                list(nodes)
            ),
            "edges": edges,
        }

        return self.dependency_graph

    def get_dependency_graph(
        self,
    ):

        return deepcopy(
            self.dependency_graph
        )

    # =========================================================
    # TIMELINE / GANTT-LIKE CONTROL
    # =========================================================

    def add_timeline_item(
        self,
        item_id,
        title,
        start_date=None,
        end_date=None,
        status="planned",
        dependencies=None,
    ):

        item = {
            "item_id": item_id,
            "title": title,
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
            "dependencies": dependencies or [],
            "created_at": self._now(),
        }

        self.timeline.append(
            item
        )

        self._touch()

        return item

    def update_timeline_item(
        self,
        item_id,
        **updates,
    ):

        for item in self.timeline:

            if item.get(
                "item_id"
            ) == item_id:

                item.update(
                    updates
                )

                item["updated_at"] = self._now()

                self._touch()

                return item

        return None

    def get_timeline(
        self,
    ):

        return deepcopy(
            self.timeline
        )

    # =========================================================
    # KNOWLEDGE GRAPH METRICS
    # =========================================================

    def update_graph_metrics(
        self,
        graph_data,
    ):

        graph_data = graph_data or {}

        objects = graph_data.get(
            "objects",
            [],
        )

        relations = graph_data.get(
            "relations",
            [],
        )

        self.knowledge_metrics = {
            "nodes": len(
                objects
            ),
            "relations": len(
                relations
            ),
            "memories": len(
                [
                    obj

                    for obj in objects

                    if obj.get(
                        "type"
                    ) == "memory"
                ]
            ),
        }

        self._touch()

        return deepcopy(
            self.knowledge_metrics
        )

    # =========================================================
    # GRAPH INTELLIGENCE SYNCHRONIZATION
    # =========================================================

    def update_graph_knowledge(
        self,
        graph_data,
    ):

        self.update_graph_metrics(
            graph_data
        )

        objects = (
            graph_data or {}
        ).get(
            "objects",
            [],
        )

        # Do not erase historical logs.
        # Rebuild graph-derived indexes separately.

        graph_decisions = []
        graph_ideas = []
        graph_artifacts = []

        for obj in objects:

            obj_type = obj.get(
                "type"
            )

            data = obj.get(
                "data",
                {},
            )

            text = data.get(
                "text",
                "",
            )

            if not text:
                continue

            if obj_type == "decision":

                graph_decisions.append(
                    {
                        "decision": text,
                        "source": "graph",
                    }
                )

            elif obj_type == "goal":

                graph_ideas.append(
                    {
                        "idea": text,
                        "source": "graph",
                        "status": "open",
                    }
                )

            elif obj_type == "artifact":

                graph_artifacts.append(
                    {
                        "artifact": text,
                        "source": "graph",
                    }
                )

        self._merge_unique_records(
            self.decision_log,
            graph_decisions,
            key_fields=[
                "decision",
                "source",
            ],
        )

        self._merge_unique_records(
            self.idea_inbox,
            graph_ideas,
            key_fields=[
                "idea",
                "source",
            ],
        )

        self._merge_unique_records(
            self.provenance_log,
            graph_artifacts,
            key_fields=[
                "artifact",
                "source",
            ],
        )

        self._touch()

        return {
            "decisions": len(
                graph_decisions
            ),
            "ideas": len(
                graph_ideas
            ),
            "artifacts": len(
                graph_artifacts
            ),
            "knowledge_metrics": deepcopy(
                self.knowledge_metrics
            ),
        }

    @staticmethod
    def _merge_unique_records(
        target,
        incoming,
        key_fields,
    ):

        existing_keys = set()

        for item in target:

            key = tuple(
                item.get(
                    field
                )

                for field in key_fields
            )

            existing_keys.add(
                key
            )

        for item in incoming:

            key = tuple(
                item.get(
                    field
                )

                for field in key_fields
            )

            if key not in existing_keys:

                target.append(
                    item
                )

                existing_keys.add(
                    key
                )

    # =========================================================
    # AUTOMATIC PROGRESS
    # =========================================================

    def _auto_update_progress(
        self,
    ):

        # Explicitly completed milestones
        completed = len(
            [
                milestone

                for milestone in self.milestones

                if milestone.get(
                    "status"
                ) == "completed"
            ]
        )

        total_milestones = len(
            self.milestones
        )

        if total_milestones > 0:

            self.progress = round(
                (
                    completed
                    / total_milestones
                )
                * 100,
                2,
            )

        else:

            # Backward-compatible fallback
            self.progress = min(
                100,
                len(
                    self.sessions
                )
                * 5,
            )

        return self.progress

    # =========================================================
    # VERSION HISTORY
    # =========================================================

    def _record_version(
        self,
        event,
        description="",
    ):

        version = {
            "version": self.VERSION,
            "event": event,
            "description": description,
            "timestamp": self._now(),
        }

        self.version_history.append(
            version
        )

        return version

    # =========================================================
    # TOUCH
    # =========================================================

    def _touch(
        self,
    ):

        self.updated_at = self._now()

    # =========================================================
    # SERIALIZATION
    # =========================================================

    def to_dict(
        self,
    ):

        return deepcopy(
            self.__dict__
        )

    # =========================================================
    # SAVE
    # =========================================================

    def save(
        self,
        directory="storage",
    ):

        os.makedirs(
            directory,
            exist_ok=True,
        )

        path = os.path.join(
            directory,
            "project.json",
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                self.to_dict(),
                f,
                indent=2,
                ensure_ascii=False,
            )

        return path

    # =========================================================
    # LOAD
    # =========================================================

    @staticmethod
    def load(
        path,
    ):

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(
                f
            )

        obj = ResearchProject(
            project_id=data.get(
                "project_id"
            ),
            title=data.get(
                "title",
                "",
            ),
            description=data.get(
                "description",
                "",
            ),
            paper_target=data.get(
                "paper_target",
                "Q1",
            ),
            repository=data.get(
                "repository",
                "",
            ),
            tags=data.get(
                "tags",
                [],
            ),
            project_path=data.get(
                "project_path"
            ),
        )

        obj.__dict__.update(
            data
        )

        # Backward compatibility
        obj._ensure_compatibility()

        return obj

    # =========================================================
    # BACKWARD COMPATIBILITY
    # =========================================================

    def _ensure_compatibility(
        self,
    ):

        defaults = {
            "sessions": [],
            "milestones": [],
            "publications": [],
            "research_ledger": [],
            "decision_log": [],
            "idea_inbox": [],
            "provenance_log": [],
            "dependencies": [],
            "dependency_graph": {
                "nodes": [],
                "edges": [],
            },
            "version_history": [],
            "timeline": [],
            "knowledge_metrics": {
                "nodes": 0,
                "relations": 0,
                "memories": 0,
            },
            "tags": [],
            "progress": 0,
            "status": "Active",
            "current_phase": "Initialization",
            "engine_version": self.VERSION,
        }

        for key, default in defaults.items():

            if not hasattr(
                self,
                key,
            ):

                setattr(
                    self,
                    key,
                    deepcopy(
                        default
                    ),
                )

        self._rebuild_dependency_graph()

    # =========================================================
    # SUMMARY
    # =========================================================

    def summary(
        self,
    ):

        return {
            "project_id": self.project_id,
            "project": self.title,
            "status": self.status,
            "phase": self.current_phase,
            "progress": self.progress,
            "sessions": len(
                self.sessions
            ),
            "goals": len(
                self.idea_inbox
            ),
            "artifacts": len(
                self.provenance_log
            ),
            "milestones": len(
                self.milestones
            ),
            "completed_milestones": len(
                [
                    milestone

                    for milestone in self.milestones

                    if milestone.get(
                        "status"
                    ) == "completed"
                ]
            ),
            "ledger_entries": len(
                self.research_ledger
            ),
            "decisions": len(
                self.decision_log
            ),
            "ideas": len(
                self.idea_inbox
            ),
            "dependencies": len(
                self.dependencies
            ),
            "timeline_items": len(
                self.timeline
            ),
            "knowledge_nodes": self.knowledge_metrics.get(
                "nodes",
                0,
            ),
            "knowledge_relations": self.knowledge_metrics.get(
                "relations",
                0,
            ),
            "memories": self.knowledge_metrics.get(
                "memories",
                0,
            ),
            "engine_version": self.VERSION,
            "updated_at": self.updated_at,
        }

    # =========================================================
    # PROJECT STATE
    # =========================================================

    def get_state(
        self,
    ):

        return {
            "project": self.to_dict(),
            "summary": self.summary(),
            "dependency_graph": self.get_dependency_graph(),
            "timeline": self.get_timeline(),
        }

