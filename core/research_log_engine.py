import os
import json
from datetime import datetime


class ResearchLogEngine:
    """
    CRME Research Log Engine v1.5.1

    Responsible for structured research evolution tracking.

    Stores:
    - Decisions
    - Goals
    - Ideas
    - Research Ledger
    - Provenance
    - Next Session Goal
    """


    def __init__(self, base_path="."):

        self.base_path = base_path

        self.session_dir = os.path.join(
            base_path,
            "memory",
            "sessions"
        )



    # =====================================================
    # INTERNAL
    # =====================================================

    def _session_path(
        self,
        session_id
    ):

        return os.path.join(
            self.session_dir,
            f"{session_id}.json"
        )



    def _load(
        self,
        session_id
    ):

        path = self._session_path(
            session_id
        )

        if not os.path.exists(path):
            return None


        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)



    def _save(
        self,
        session_id,
        session
    ):

        path = self._session_path(
            session_id
        )


        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                session,
                f,
                indent=2,
                ensure_ascii=False
            )



    def _ensure_research_block(
        self,
        session
    ):

        if "research" not in session:

            session["research"] = {}


        defaults = {

            "decisions": [],

            "goals": [],

            "ideas": [],

            "ledger": [],

            "provenance": [],

            "next_goal": ""

        }


        for key, value in defaults.items():

            if key not in session["research"]:

                session["research"][key] = value



    def _append(
        self,
        session_id,
        section,
        text
    ):

        session = self._load(
            session_id
        )


        if not session:

            return False


        self._ensure_research_block(
            session
        )


        session["research"][section].append(

            {

                "text":
                    text,

                "timestamp":
                    datetime.utcnow().isoformat()

            }

        )


        session["updated_at"] = (
            datetime.utcnow().isoformat()
        )


        self._save(
            session_id,
            session
        )


        return True



    # =====================================================
    # PUBLIC METHODS
    # =====================================================


    def add_decision(
        self,
        session_id,
        decision
    ):

        return self._append(
            session_id,
            "decisions",
            decision
        )



    def add_goal(
        self,
        session_id,
        goal
    ):

        return self._append(
            session_id,
            "goals",
            goal
        )



    def add_idea(
        self,
        session_id,
        idea
    ):

        return self._append(
            session_id,
            "ideas",
            idea
        )



    def add_ledger_entry(
        self,
        session_id,
        entry
    ):

        return self._append(
            session_id,
            "ledger",
            entry
        )



    def add_provenance(
        self,
        session_id,
        source
    ):

        return self._append(
            session_id,
            "provenance",
            source
        )



    def set_next_goal(
        self,
        session_id,
        goal
    ):

        session = self._load(
            session_id
        )


        if not session:

            return False


        self._ensure_research_block(
            session
        )


        session["research"]["next_goal"] = goal


        session["updated_at"] = (
            datetime.utcnow().isoformat()
        )


        self._save(
            session_id,
            session
        )


        return True



    def get_research_state(
        self,
        session_id
    ):

        session = self._load(
            session_id
        )


        if not session:

            return None


        self._ensure_research_block(
            session
        )


        return session["research"]

