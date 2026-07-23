import os
import json
from datetime import datetime



class ContextEngine:
    """
    CRME Context Transfer Engine v1.0

    Creates portable research context packages.

    Includes:

    - Project state
    - Sessions
    - Decisions
    - Goals
    - Artifacts
    - Knowledge Graph
    """



    def __init__(
        self,
        project,
        graph,
        session_engine=None
    ):

        self.project = project
        self.graph = graph
        self.session_engine = session_engine



    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    def build_context(self):


        graph_data = self.graph.export()


        objects = graph_data.get(
            "objects",
            []
        )


        decisions = []
        goals = []
        artifacts = []
        memories = []



        for obj in objects:


            obj_type = obj.get(
                "type"
            )


            data = obj.get(
                "data",
                {}
            )


            if obj_type == "decision":

                decisions.append(
                    data
                )


            elif obj_type == "goal":

                goals.append(
                    data
                )


            elif obj_type == "artifact":

                artifacts.append(
                    data
                )


            elif obj_type == "memory":

                memories.append(
                    data
                )



        return {


            "crme_version":
                "1.0",


            "generated_at":
                datetime.utcnow().isoformat(),


            "project":
                self.project.to_dict(),


            "summary":
                self.project.summary(),


            "research_state":
            {

                "decisions":
                    decisions,

                "goals":
                    goals,

                "artifacts":
                    artifacts,

                "memories":
                    memories

            },


            "knowledge_graph":
                graph_data,


            "transfer_info":
            {

                "purpose":
                    "Transfer CRME research state between LLM systems",


                "current_stage":
                    "Semantic Query Engine Completed",


                "next_stage":
                    "Autonomous Context Intelligence"

            }

        }



    # =====================================================
    # EXPORT
    # =====================================================

    def export(
        self,
        path="exports/CRME_Context_Transfer.json"
    ):


        os.makedirs(
            os.path.dirname(path),
            exist_ok=True
        )


        context = self.build_context()


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


        return path

