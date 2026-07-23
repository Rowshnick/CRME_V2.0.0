import json
from datetime import datetime


class IntelligenceEngine:
    """
    CRME Autonomous Context Intelligence Engine v1.3

    Responsible for:
    - Research state analysis
    - Knowledge gap detection
    - Insight generation
    - Next action recommendation
    """

    def __init__(
        self,
        project,
        graph
    ):

        self.project = project
        self.graph = graph



    # =====================================================
    # COLLECT STATE
    # =====================================================

    def collect_state(self):

        graph_data = self.graph.export()

        objects = graph_data.get(
            "objects",
            []
        )


        return {

            "project":
                self.project.to_dict(),


            "summary":
                self.project.summary(),


            "nodes":
                len(objects),


            "relations":
                len(
                    graph_data.get(
                        "relations",
                        []
                    )
                ),

            "objects":
                objects

        }



    # =====================================================
    # INSIGHT GENERATION
    # =====================================================

    def generate_insights(self):

        state = self.collect_state()

        insights = []


        summary = state["summary"]


        if summary.get("knowledge_nodes", 0) > 0:

            insights.append(
                "Knowledge Graph is active and contains research entities."
            )


        if summary.get("decisions", 0) > 0:

            insights.append(
                "Research decisions are being captured."
            )


        if summary.get("goals", 0) > 0:

            insights.append(
                "Research objectives have been defined."
            )


        if summary.get("artifacts", 0) == 0:

            insights.append(
                "No research artifacts are connected yet."
            )


        return insights



    # =====================================================
    # KNOWLEDGE GAP ANALYSIS
    # =====================================================

    def detect_gaps(self):

        gaps = []

        summary = self.project.summary()


        if summary.get(
            "milestones",
            0
        ) == 0:

            gaps.append(
                "Research milestone planning is missing."
            )


        if summary.get(
            "artifacts",
            0
        ) == 0:

            gaps.append(
                "No research artifacts documented."
            )


        if summary.get(
            "goals",
            0
        ) == 0:

            gaps.append(
                "Research goals are undefined."
            )


        return gaps



    # =====================================================
    # NEXT ACTION
    # =====================================================

    def recommend_actions(self):

        actions = []

        summary = self.project.summary()


        if summary.get(
            "milestones",
            0
        ) == 0:

            actions.append(
                "Create first research milestone."
            )


        if summary.get(
            "artifacts",
            0
        ) < 5:

            actions.append(
                "Create architecture and documentation artifacts."
            )


        if summary.get(
            "knowledge_nodes",
            0
        ) > 0:

            actions.append(
                "Expand semantic knowledge connections."
            )


        actions.append(
            "Implement Autonomous Context Intelligence layer."
        )


        return actions



    # =====================================================
    # FULL ANALYSIS
    # =====================================================

    def analyze(self):

        return {

            "generated_at":
                datetime.utcnow().isoformat(),


            "insights":
                self.generate_insights(),


            "knowledge_gaps":
                self.detect_gaps(),


            "recommended_actions":
                self.recommend_actions()

        }

