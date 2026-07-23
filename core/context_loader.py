import json
import os

from core.context_schema import ContextSchema



class ContextLoader:
    """
    CRME Context Loader v1.0

    Restores CRME state from
    CRME_Context_Transfer.json
    """



    def __init__(
        self,
        base_path="."
    ):

        self.base_path = base_path

        self.storage_path = os.path.join(
            base_path,
            "storage"
        )

        os.makedirs(
            self.storage_path,
            exist_ok=True
        )



    # =====================================================
    # LOAD CONTEXT
    # =====================================================

    def load(
        self,
        path
    ):


        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            context = json.load(f)



        validation = (
            ContextSchema.validate(
                context
            )
        )


        if not validation["valid"]:

            raise ValueError(
                f"Invalid CRME Context: {validation}"
            )



        return context



    # =====================================================
    # RESTORE PROJECT
    # =====================================================

    def restore_project(
        self,
        context
    ):


        path = os.path.join(
            self.storage_path,
            "project.json"
        )


        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:


            json.dump(
                context["project"],
                f,
                indent=2,
                ensure_ascii=False
            )


        return path



    # =====================================================
    # RESTORE GRAPH
    # =====================================================

    def restore_graph(
        self,
        context
    ):


        path = os.path.join(
            self.storage_path,
            "graph.json"
        )


        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:


            json.dump(
                context["knowledge_graph"],
                f,
                indent=2,
                ensure_ascii=False
            )


        return path



    # =====================================================
    # FULL RESTORE
    # =====================================================

    def restore(
        self,
        path
    ):


        context = self.load(
            path
        )


        project_file = self.restore_project(
            context
        )


        graph_file = self.restore_graph(
            context
        )



        return {

            "status":
                "restored",


            "project":
                project_file,


            "graph":
                graph_file,


            "version":
                context["crme_version"]

        }

