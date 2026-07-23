import os
import json
from datetime import datetime, timezone
from copy import deepcopy

from core.change_tracking_engine import ChangeTrackingEngine


class SessionEngine:
    """
    CRME Session Engine v1.6

    Responsibilities
    ----------------

    - Create research sessions
    - Store session state
    - Manage research memory
    - Generate human-readable research reports
    - Maintain research provenance
    - Maintain session continuity
    - Track state transitions
    - Integrate with ChangeTrackingEngine
    - Preserve before/after state history
    - Track added, removed and modified items
    - Track structural and fundamental changes

    Architecture
    ------------

        SESSION STATE
              │
              ▼
        BEFORE STATE
              │
              ▼
        SESSION UPDATE
              │
              ▼
        AFTER STATE
              │
              ▼
        ChangeTrackingEngine
              │
              ├── ADDED
              ├── REMOVED
              ├── MODIFIED
              ├── STRUCTURAL
              └── FUNDAMENTAL
                    │
                    ▼
              Persistent Change History

    Core Principle
    --------------

    Every meaningful session update should be represented as:

        Previous Session State
                +
        New Session State
                +
        Session Provenance
                +
        Decision Context
                =
        Reproducible Session Evolution
    """

    VERSION = "1.6.0"

    def __init__(
        self,
        base_path,
        project=None,
        change_tracking_engine=None
    ):

        self.base_path = base_path

        self.project = project

        self.session_dir = os.path.join(
            base_path,
            "memory",
            "sessions"
        )

        os.makedirs(
            self.session_dir,
            exist_ok=True
        )

        # =====================================================
        # CHANGE TRACKING INTEGRATION
        # =====================================================

        if change_tracking_engine:

            self.change_tracking_engine = (
                change_tracking_engine
            )

        else:

            self.change_tracking_engine = (
                ChangeTrackingEngine(
                    base_path=base_path
                )
            )

    # =========================================================
    # TIME
    # =========================================================

    def _now(self):

        return datetime.now(
            timezone.utc
        ).isoformat()

    # =========================================================
    # CREATE SESSION
    # =========================================================

    def create_session(
        self,
        project_id=None,
        metadata=None
    ):

        session_id = (

            f"S-"
            f"{datetime.now(timezone.utc).strftime(
                '%Y%m%d%H%M%S%f'
            )}"

        )

        now = self._now()

        session = {

            "session_id": session_id,

            "project_id": project_id,

            "created_at": now,

            "updated_at": now,

            "metadata": metadata or {},

            "state": {

                "messages": [],

                "decisions": [],

                "goals": [],

                "artifacts": [],

                "notes": []

            },

            "research": {

                "summary": "",

                "ledger": [],

                "decisions": [],

                "ideas": [],

                "provenance": [],

                "next_goal": "",

                "changes": {

                    "total_changes": 0,

                    "added": 0,

                    "removed": 0,

                    "modified": 0,

                    "fundamental": 0,

                    "structural": 0,

                    "item_added": 0,

                    "item_removed": 0,

                    "item_unchanged": 0

                },

                "change_ids": []

            },

            "version": 2,

            "engine_version": self.VERSION

        }

        self.save_session(
            session_id,
            session
        )

        return session_id

    # =========================================================
    # LOAD SESSION
    # =========================================================

    def load_session(
        self,
        session_id
    ):

        return self.get_snapshot(
            session_id
        )

    # =========================================================
    # SESSION STATE EXTRACTION
    # =========================================================

    def _extract_tracking_state(
        self,
        session
    ):

        if not session:

            return {}

        return {

            "session_id": session.get(
                "session_id"
            ),

            "project_id": session.get(
                "project_id"
            ),

            "metadata": deepcopy(
                session.get(
                    "metadata",
                    {}
                )
            ),

            "state": deepcopy(
                session.get(
                    "state",
                    {}
                )
            ),

            "research": deepcopy(
                session.get(
                    "research",
                    {}
                )
            ),

            "version": session.get(
                "version"
            )

        }

    # =========================================================
    # UPDATE SESSION
    # =========================================================

    def update_session(
        self,
        session_id,
        update,
        description="Session state updated",
        decision_ids=None,
        related_goals=None,
        related_artifacts=None,
        affected_files=None
    ):

        session = self.load_session(
            session_id
        )

        if not session:

            return False

        # -----------------------------------------------------
        # BEFORE STATE
        # -----------------------------------------------------

        before_session = deepcopy(
            session
        )

        before_state = (
            self._extract_tracking_state(
                before_session
            )
        )

        state = session.get(
            "state",
            {}
        )

        # -----------------------------------------------------
        # APPLY UPDATE
        # -----------------------------------------------------

        for key, value in update.items():

            if (

                key in state

                and isinstance(
                    state[key],
                    list
                )

            ):

                if isinstance(
                    value,
                    list
                ):

                    state[key].extend(
                        deepcopy(
                            value
                        )
                    )

                else:

                    state[key].append(
                        deepcopy(
                            value
                        )
                    )

            else:

                state[key] = deepcopy(
                    value
                )

        session["state"] = state

        session["updated_at"] = (
            self._now()
        )

        session["version"] = (
            session.get(
                "version",
                0
            )
            + 1
        )

        # -----------------------------------------------------
        # AFTER STATE
        # -----------------------------------------------------

        after_session = deepcopy(
            session
        )

        after_state = (
            self._extract_tracking_state(
                after_session
            )
        )

        # -----------------------------------------------------
        # CHANGE DETECTION
        # -----------------------------------------------------

        comparison = (
            self.change_tracking_engine.compare_snapshots(
                before_state,
                after_state
            )
        )

        change_result = None

        if comparison.get(
            "changed"
        ):

            event = (
                self.change_tracking_engine.create_change_event(

                    before=before_state,

                    after=after_state,

                    session_id=session_id,

                    decision_ids=decision_ids,

                    description=description,

                    source="session_update",

                    affected_files=affected_files,

                    related_goals=related_goals,

                    related_artifacts=related_artifacts

                )
            )

            change_result = (
                self.change_tracking_engine.record_change(
                    event
                )
            )

            # -------------------------------------------------
            # SAVE CHANGE REFERENCES INSIDE SESSION
            # -------------------------------------------------

            research = session.setdefault(
                "research",
                {}
            )

            changes = research.setdefault(
                "changes",
                {}
            )

            summary = comparison.get(
                "summary",
                {}
            )

            changes["total_changes"] = (
                changes.get(
                    "total_changes",
                    0
                )
                + summary.get(
                    "total_changes",
                    0
                )
            )

            changes["added"] = (
                changes.get(
                    "added",
                    0
                )
                + summary.get(
                    "added",
                    0
                )
            )

            changes["removed"] = (
                changes.get(
                    "removed",
                    0
                )
                + summary.get(
                    "removed",
                    0
                )
            )

            changes["modified"] = (
                changes.get(
                    "modified",
                    0
                )
                + summary.get(
                    "modified",
                    0
                )
            )

            changes["fundamental"] = (
                changes.get(
                    "fundamental",
                    0
                )
                + summary.get(
                    "fundamental",
                    0
                )
            )

            changes["structural"] = (
                changes.get(
                    "structural",
                    0
                )
                + summary.get(
                    "structural",
                    0
                )
            )

            changes["item_added"] = (
                changes.get(
                    "item_added",
                    0
                )
                + summary.get(
                    "item_added",
                    0
                )
            )

            changes["item_removed"] = (
                changes.get(
                    "item_removed",
                    0
                )
                + summary.get(
                    "item_removed",
                    0
                )
            )

            changes["item_unchanged"] = (
                changes.get(
                    "item_unchanged",
                    0
                )
                + summary.get(
                    "item_unchanged",
                    0
                )
            )

            change_ids = research.setdefault(
                "change_ids",
                []
            )

            change_id = event.get(
                "change_id"
            )

            if (

                change_id

                and change_id not in change_ids

            ):

                change_ids.append(
                    change_id
                )

        # -----------------------------------------------------
        # SAVE SESSION
        # -----------------------------------------------------

        self.save_session(
            session_id,
            session
        )

        return {

            "success": True,

            "session_id": session_id,

            "changed": comparison.get(
                "changed",
                False
            ),

            "comparison": comparison,

            "change": change_result,

            "session": session

        }

    # =========================================================
    # SAVE SESSION
    # =========================================================

    def save_session(
        self,
        session_id,
        data
    ):

        path = os.path.join(

            self.session_dir,

            f"{session_id}.json"

        )

        with open(

            path,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                data,

                f,

                indent=2,

                ensure_ascii=False

            )

    # =========================================================
    # GET SNAPSHOT
    # =========================================================

    def get_snapshot(
        self,
        session_id
    ):

        path = os.path.join(

            self.session_dir,

            f"{session_id}.json"

        )

        if not os.path.exists(
            path
        ):

            return None

        with open(

            path,

            "r",

            encoding="utf-8"

        ) as f:

            return json.load(
                f
            )

    # =========================================================
    # BUILD RESEARCH SUMMARY
    # =========================================================

    def build_summary(
        self,
        session
    ):

        state = session.get(
            "state",
            {}
        )

        changes = (

            session.get(
                "research",
                {}
            ).get(
                "changes",
                {}
            )

        )

        summary = (

            f"Session "
            f"{session['session_id']} "
            f"contains "
            f"{len(state.get('messages', []))} "
            f"messages, "
            f"{len(state.get('decisions', []))} "
            f"decisions, "
            f"{len(state.get('goals', []))} "
            f"goals. "

            f"Tracked changes: "
            f"{changes.get('total_changes', 0)}. "

            f"Added: "
            f"{changes.get('added', 0)}. "

            f"Removed: "
            f"{changes.get('removed', 0)}. "

            f"Modified: "
            f"{changes.get('modified', 0)}. "

            f"Fundamental: "
            f"{changes.get('fundamental', 0)}. "

            f"Structural: "
            f"{changes.get('structural', 0)}."

        )

        return summary

    # =========================================================
    # GENERATE MARKDOWN REPORT
    # =========================================================

    def generate_markdown_report(
        self,
        session_id
    ):

        session = self.load_session(
            session_id
        )

        if not session:

            return None

        research = session.get(
            "research",
            {}
        )

        changes = research.get(
            "changes",
            {}
        )

        change_ids = research.get(
            "change_ids",
            []
        )

        path = os.path.join(

            self.session_dir,

            f"{session_id}.md"

        )

        content = (

            "# CRME Research Session Report\n\n"

            "## Session Metadata\n\n"

            f"- Session ID: "
            f"{session.get('session_id')}\n"

            f"- Project: "
            f"{session.get('project_id')}\n"

            f"- Created: "
            f"{session.get('created_at')}\n"

            f"- Updated: "
            f"{session.get('updated_at')}\n"

            f"- Version: "
            f"{session.get('version')}\n"

            f"- Engine Version: "
            f"{session.get('engine_version')}\n\n"

            "## Research Summary\n\n"

            f"{research.get('summary', '')}\n\n"

            "## Change Summary\n\n"

            f"- Total changes: "
            f"{changes.get('total_changes', 0)}\n"

            f"- Added: "
            f"{changes.get('added', 0)}\n"

            f"- Removed: "
            f"{changes.get('removed', 0)}\n"

            f"- Modified: "
            f"{changes.get('modified', 0)}\n"

            f"- Fundamental: "
            f"{changes.get('fundamental', 0)}\n"

            f"- Structural: "
            f"{changes.get('structural', 0)}\n"

            f"- Item additions: "
            f"{changes.get('item_added', 0)}\n"

            f"- Item removals: "
            f"{changes.get('item_removed', 0)}\n"

            f"- Unchanged items: "
            f"{changes.get('item_unchanged', 0)}\n\n"

            "## Change Event IDs\n\n"

        )

        for change_id in change_ids:

            content += (

                f"- `{change_id}`\n"

            )

        content += (

            "\n\n"

            "## Research Ledger Entry\n\n"

        )

        for item in research.get(
            "ledger",
            []
        ):

            content += (

                f"- {item}\n"

            )

        content += (

            "\n\n"

            "## Decision Log Entry\n\n"

        )

        for item in research.get(
            "decisions",
            []
        ):

            content += (

                f"- {item}\n"

            )

        content += (

            "\n\n"

            "## Idea Inbox Entry\n\n"

        )

        for item in research.get(
            "ideas",
            []
        ):

            content += (

                f"- {item}\n"

            )

        content += (

            "\n\n"

            "## Research Provenance\n\n"

        )

        for item in research.get(
            "provenance",
            []
        ):

            content += (

                f"- {item}\n"

            )

        content += (

            "\n\n"

            "## Next Session Goal\n\n"

            f"{research.get('next_goal', '')}\n"

        )

        with open(

            path,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(
                content
            )

        return path

    # =========================================================
    # FINALIZE SESSION
    # =========================================================

    def finalize_session(
        self,
        session_id
    ):

        session = self.load_session(
            session_id
        )

        if not session:

            return False

        session["research"]["summary"] = (

            self.build_summary(
                session
            )

        )

        session["updated_at"] = (
            self._now()
        )

        self.save_session(

            session_id,

            session

        )

        report = (

            self.generate_markdown_report(

                session_id

            )

        )

        return {

            "session": session_id,

            "report": report,

            "change_summary": (

                session.get(
                    "research",
                    {}
                ).get(
                    "changes",
                    {}
                )

            ),

            "change_ids": (

                session.get(
                    "research",
                    {}
                ).get(
                    "change_ids",
                    []
                )

            )

        }

    # =========================================================
    # LIST SESSIONS
    # =========================================================

    def list_sessions(
        self
    ):

        sessions = []

        for file in os.listdir(
            self.session_dir
        ):

            if file.endswith(
                ".json"
            ):

                sid = file.replace(
                    ".json",
                    ""
                )

                snapshot = self.get_snapshot(
                    sid
                )

                if snapshot:

                    sessions.append(
                        snapshot
                    )

        return sessions

    # =========================================================
    # BIND PROJECT
    # =========================================================

    def bind_to_project(
        self,
        session_id,
        project_id
    ):

        session = self.load_session(
            session_id
        )

        if not session:

            return False

        before_session = deepcopy(
            session
        )

        before_state = (
            self._extract_tracking_state(
                before_session
            )
        )

        session["project_id"] = (
            project_id
        )

        session["updated_at"] = (
            self._now()
        )

        session["version"] = (

            session.get(
                "version",
                0
            )

            + 1

        )

        after_session = deepcopy(
            session
        )

        after_state = (
            self._extract_tracking_state(
                after_session
            )
        )

        comparison = (
            self.change_tracking_engine.compare_snapshots(
                before_state,
                after_state
            )
        )

        if comparison.get(
            "changed"
        ):

            event = (
                self.change_tracking_engine.create_change_event(

                    before=before_state,

                    after=after_state,

                    session_id=session_id,

                    description=(
                        "Session bound to project"
                    ),

                    source="session_binding"

                )
            )

            result = (
                self.change_tracking_engine.record_change(
                    event
                )
            )

            research = session.setdefault(
                "research",
                {}
            )

            change_ids = research.setdefault(
                "change_ids",
                []
            )

            change_id = event.get(
                "change_id"
            )

            if (

                change_id

                and change_id not in change_ids

            ):

                change_ids.append(
                    change_id
                )

        self.save_session(
            session_id,
            session
        )

        return True

    # =========================================================
    # CHANGE HISTORY API
    # =========================================================

    def get_session_changes(
        self,
        session_id
    ):

        return (

            self.change_tracking_engine.get_session_changes(

                session_id

            )

        )

    def get_session_change_summary(
        self,
        session_id
    ):

        changes = self.get_session_changes(
            session_id
        )

        summary = {

            "session_id": session_id,

            "total_events": len(
                changes
            ),

            "total_changes": 0,

            "added": 0,

            "removed": 0,

            "modified": 0,

            "fundamental": 0,

            "structural": 0,

            "item_added": 0,

            "item_removed": 0,

            "item_unchanged": 0

        }

        for event in changes:

            event_summary = event.get(
                "summary",
                {}
            )

            for key in [

                "total_changes",

                "added",

                "removed",

                "modified",

                "fundamental",

                "structural",

                "item_added",

                "item_removed",

                "item_unchanged"

            ]:

                summary[key] += (

                    event_summary.get(
                        key,
                        0
                    )

                )

        return summary

    # =========================================================
    # SESSION CONTINUITY
    # =========================================================

    def get_continuation_context(
        self,
        session_id
    ):

        session = self.load_session(
            session_id
        )

        if not session:

            return None

        changes = (

            self.get_session_changes(
                session_id
            )

        )

        return {

            "session_id": session_id,

            "project_id": session.get(
                "project_id"
            ),

            "latest_state": deepcopy(
                session.get(
                    "state",
                    {}
                )
            ),

            "research": deepcopy(
                session.get(
                    "research",
                    {}
                )
            ),

            "changes": changes,

            "change_summary": (

                self.get_session_change_summary(
                    session_id
                )

            ),

            "next_goal": (

                session.get(
                    "research",
                    {}
                ).get(
                    "next_goal",
                    ""
                )

            )

        }
