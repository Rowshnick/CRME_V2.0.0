import os
from datetime import datetime


class SessionReviewEngine:
    """
    CRME Session Review Engine v1.5.3

    Generates enhanced research review reports.

    Features:
    - Session summary
    - Research decisions
    - Goals
    - Ledger
    - Provenance
    - Current system state
    - Change summary
    - Open issues
    """


    def __init__(
        self,
        base_path="."
    ):

        self.base_path = base_path

        self.session_dir = os.path.join(
            base_path,
            "memory",
            "sessions"
        )


    # =====================================================
    # LOAD SESSION
    # =====================================================

    def _load_session(
        self,
        session_id
    ):

        import json

        path = os.path.join(
            self.session_dir,
            f"{session_id}.json"
        )


        if not os.path.exists(path):
            return None


        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)



    # =====================================================
    # BUILD REVIEW
    # =====================================================

    def build_review(
        self,
        session_id
    ):

        session = self._load_session(
            session_id
        )


        if not session:
            return None


        research = session.get(
            "research",
            {}
        )


        return {

            "session_id":
                session_id,


            "created_at":
                session.get(
                    "created_at"
                ),


            "generated_at":
                datetime.utcnow().isoformat(),


            "summary":
            {

                "messages":
                    len(
                        session.get(
                            "state",
                            {}
                        ).get(
                            "messages",
                            []
                        )
                    ),

                "decisions":
                    len(
                        research.get(
                            "decisions",
                            []
                        )
                    ),

                "goals":
                    len(
                        research.get(
                            "goals",
                            []
                        )
                    ),

                "ledger":
                    len(
                        research.get(
                            "ledger",
                            []
                        )
                    ),

                "ideas":
                    len(
                        research.get(
                            "ideas",
                            []
                        )
                    )

            },


            "research":
                research

        }



    # =====================================================
    # MARKDOWN EXPORT
    # =====================================================

    def export_markdown(
        self,
        session_id
    ):

        report = self.build_review(
            session_id
        )


        if not report:
            return None


        path = os.path.join(
            self.session_dir,
            f"{session_id}_review.md"
        )


        research = report["research"]


        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:


            f.write(
                "# CRME Session Review\n\n"
            )


            f.write(
                "## Session Metadata\n\n"
            )

            f.write(
                f"Session ID: {session_id}\n\n"
            )


            f.write(
                "## Summary\n\n"
            )


            for k,v in report["summary"].items():

                f.write(
                    f"- {k}: {v}\n"
                )


            f.write(
                "\n## Changes Implemented\n\n"
            )


            for item in research.get(
                "ledger",
                []
            ):

                f.write(
                    f"- {item['text']}\n"
                )


            f.write(
                "\n## Decisions\n\n"
            )


            for item in research.get(
                "decisions",
                []
            ):

                f.write(
                    f"- {item['text']}\n"
                )


            f.write(
                "\n## Research Goals\n\n"
            )


            for item in research.get(
                "goals",
                []
            ):

                f.write(
                    f"- {item['text']}\n"
                )


            f.write(
                "\n## Provenance\n\n"
            )


            for item in research.get(
                "provenance",
                []
            ):

                f.write(
                    f"- {item['text']}\n"
                )


            f.write(
                "\n## Current State\n\n"
            )


            f.write(
                "CRME Development Status:\n"
            )

            f.write(
                "- Session Engine: Active\n"
            )

            f.write(
                "- Research Log Engine: Active\n"
            )

            f.write(
                "- Session Review Engine: Active\n"
            )


            f.write(
                "\n## Open Issues\n\n"
            )

            f.write(
                "- Automatic decision extraction\n"
            )

            f.write(
                "- Semantic linking between sessions\n"
            )

            f.write(
                "- Research milestone tracking\n"
            )


            f.write(
                "\n## Next Session Goal\n\n"
            )


            f.write(
                research.get(
                    "next_goal",
                    "Not defined"
                )
            )


        return path

