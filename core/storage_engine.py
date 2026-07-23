import os
import json


class StorageEngine:
    """
    CRME Persistent Storage Layer

    Responsible for:
    - Saving project state
    - Loading project state
    - Saving graph state
    - Managing storage paths
    """


    def __init__(self, base_path="."):

        self.storage_path = os.path.join(
            base_path,
            "storage"
        )

        self.sessions_path = os.path.join(
            self.storage_path,
            "sessions"
        )


        os.makedirs(
            self.sessions_path,
            exist_ok=True
        )


        self.project_file = os.path.join(
            self.storage_path,
            "project.json"
        )


        self.graph_file = os.path.join(
            self.storage_path,
            "graph.json"
        )



    # ==========================================
    # PROJECT
    # ==========================================

    def save_project(self, data):

        with open(
            self.project_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )


    def load_project(self):

        if not os.path.exists(
            self.project_file
        ):

            return None


        with open(
            self.project_file,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)



    # ==========================================
    # GRAPH
    # ==========================================

    def save_graph(self, data):

        with open(
            self.graph_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )



    def load_graph(self):

        if not os.path.exists(
            self.graph_file
        ):

            return {
                "objects": [],
                "relations": []
            }


        with open(
            self.graph_file,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)



    # ==========================================
    # STATUS
    # ==========================================

    def info(self):

        return {

            "storage":
                self.storage_path,

            "project_exists":
                os.path.exists(
                    self.project_file
                ),

            "graph_exists":
                os.path.exists(
                    self.graph_file
                )

        }
