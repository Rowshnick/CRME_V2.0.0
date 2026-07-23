import os

from core.project_engine import ResearchProject
from core.session_engine import SessionEngine
from core.memory_engine import MemoryEngine
from core.graph_engine import GraphEngine
from core.crme_kernel import CRMEKernel
from core.storage_engine import StorageEngine



class CRMEBootstrap:
    """
    CRME Persistent Runtime Bootstrap

    Responsible for:

    - Loading / creating project state
    - Loading persistent graph state
    - Synchronizing knowledge
    - Initializing CRME Kernel
    """



    def __init__(
        self,
        project_id="CRME-001",
        title="CRME Research Core",
        base_path="."
    ):

        self.project_id = project_id
        self.title = title
        self.base_path = base_path


        self.storage = StorageEngine(
            base_path
        )


        self.project = None
        self.session = None
        self.memory = None
        self.graph = None
        self.kernel = None



    # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize(self):


        # -------------------------
        # Load / Create Project
        # -------------------------

        project_data = self.storage.load_project()



        if project_data:


            self.project = ResearchProject.load(
                self.storage.project_file
            )


        else:


            self.project = ResearchProject(
                self.project_id,
                self.title
            )


            self.save_project()



        # -------------------------
        # Session Engine
        # -------------------------

        self.session = SessionEngine(
            self.base_path,
            self.project
        )



        # -------------------------
        # Memory Engine
        # -------------------------

        self.memory = MemoryEngine()



        # -------------------------
        # Graph Engine
        # -------------------------

        self.graph = GraphEngine()



        graph_data = self.storage.load_graph()



        if graph_data:


            self.graph.index = {

                "objects":
                    graph_data.get(
                        "objects",
                        []
                    ),


                "relations":
                    graph_data.get(
                        "relations",
                        []
                    )

            }



        # -------------------------
        # Knowledge Synchronization
        # -------------------------

        self.project.update_graph_knowledge(
            self.graph.export()
        )



        # -------------------------
        # Kernel
        # -------------------------

        self.kernel = CRMEKernel(

            self.session,

            self.project,

            self.memory,

            self.graph

        )


        return self.kernel



    # =====================================================
    # SAVE STATE
    # =====================================================

    def save_project(self):

        if self.project:


            self.storage.save_project(

                self.project.to_dict()

            )



    def save_graph(self):

        if self.graph:


            self.storage.save_graph(

                self.graph.export()

            )



    # =====================================================
    # STATUS
    # =====================================================

    def status(self):


        return {


            "status":
                "Running",


            "project":
                self.project.title,


            "progress":
                self.project.progress,


            "sessions":
                len(
                    self.project.sessions
                ),


            "knowledge_nodes":
                len(
                    self.graph.export()["objects"]
                )

        }



# =========================================================
# MODULE ENTRY
# =========================================================

def main():


    runtime = CRMEBootstrap()


    runtime.initialize()



    print(
        "================================"
    )


    print(
        " CRME Persistent Runtime Started "
    )


    print(
        "================================"
    )


    print(
        runtime.status()
    )



if __name__ == "__main__":

    main()

