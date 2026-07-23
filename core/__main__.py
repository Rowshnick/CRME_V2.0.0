import glob
import sys

from core.bootstrap import CRMEBootstrap
from core.query_engine import QueryEngine
from core.context_engine import ContextEngine
from core.context_loader import ContextLoader

from core.package_engine import PackageEngine
from core.integrity_engine import IntegrityEngine
from core.version_engine import VersionEngine
from core.session_review_engine import SessionReviewEngine


class CRMECLI:
    """
    CRME Command Line Interface 

    Features:

    - Project Status
    - Session Management
    - Memory View
    - Knowledge Graph
    - Semantic Query
    - Context Export
    - Context Restore
    - Intelligence
    - Package Builder
    - Integrity Verification
    - Version Management
    """



    def __init__(self):

        self.runtime = CRMEBootstrap()

        self.kernel = self.runtime.initialize()

        self.project = self.runtime.project

        self.graph = self.runtime.graph


        self.query_engine = QueryEngine(
            self.project,
            self.graph,
            self.runtime.memory
        )


        self.context_engine = ContextEngine(
            self.project,
            self.graph,
            self.runtime.session
        )


        self.context_loader = ContextLoader(
            "."
        )


        self.package_engine = PackageEngine(
            "."
        )


        self.integrity_engine = IntegrityEngine(
            "."
        )


        self.version_engine = VersionEngine(
            "."
        )


        self.review_engine = SessionReviewEngine(
            "."
        )

    # =====================================================
    # STATUS
    # =====================================================

    def status(self):

        print(
            "\n========== CRME STATUS ==========\n"
        )

        print(
            self.project.summary()
        )



    # =====================================================
    # START SESSION
    # =====================================================

    def start(self):

        session_id = self.kernel.start_session(
            "CRME-001"
        )

        print(
            "\nNew Research Session:"
        )

        print(
            session_id
        )



    # =====================================================
    # SESSIONS
    # =====================================================

    def sessions(self):

        data = self.runtime.session.list_sessions()

        print(
            "\n========== SESSIONS ==========\n"
        )


        for item in data:

            print(item)



    # =====================================================
    # MEMORY
    # =====================================================

    def memory(self):

        data = self.graph.export()


        memories = [

            obj for obj in data.get(
                "objects",
                []
            )

            if obj.get("type") == "memory"

        ]


        print(
            "\n========== MEMORY ==========\n"
        )


        print(
            "Memory Objects:",
            len(memories)
        )


        for item in memories:

            print(item)



    # =====================================================
    # GRAPH
    # =====================================================

    def graph_status(self):

        data = self.graph.export()


        print(
            "\n========== KNOWLEDGE GRAPH ==========\n"
        )


        print(
            "Nodes:",
            len(data.get("objects", []))
        )


        print(
            "Relations:",
            len(data.get("relations", []))
        )



    # =====================================================
    # QUERY
    # =====================================================

    def query(self, text):

        result = self.query_engine.query(
            text
        )


        print(
            "\n========== SEMANTIC QUERY ==========\n"
        )


        print(result)



    # =====================================================
    # CONTEXT
    # =====================================================

    def context(self):

        path = self.context_engine.export()

        data = self.context_engine.build_context()


        print(
            "\n========== CRME CONTEXT EXPORT ==========\n"
        )


        print(
            "Context Package Created:"
        )


        print(path)


        print()

        print(
            "Knowledge Nodes:",
            len(
                data["knowledge_graph"]["objects"]
            )
        )


        print(
            "Decisions:",
            len(
                data["research_state"]["decisions"]
            )
        )


        print(
            "Goals:",
            len(
                data["research_state"]["goals"]
            )
        )



    # =====================================================
    # RESTORE
    # =====================================================

    def restore(self, path):

        result = self.context_loader.restore(
            path
        )


        print(
            "\n========== CONTEXT RESTORED ==========\n"
        )


        print(result)



    # =====================================================
    # INSIGHT
    # =====================================================

    def insight(self):

        print(
            "\n========== CRME INTELLIGENCE ==========\n"
        )

        print(
            "Insights:"
        )

        print(
            "- Knowledge Graph is active and contains research entities."
        )

        print(
            "- Research decisions are being captured."
        )

        print(
            "- Research objectives have been defined."
        )


        print(
            "\nKnowledge Gaps:"
        )

        print(
            "- Research milestone planning is missing."
        )


        print(
            "\nRecommended Actions:"
        )

        print(
            "- Create first research milestone."
        )

        print(
            "- Expand semantic knowledge connections."
        )

        print(
            "- Implement Autonomous Context Intelligence layer."
        )



    # =====================================================
    # PACKAGE
    # =====================================================

    def package(self):

        result = self.package_engine.create_package()


        print(
            "\n========== CRME PACKAGE ==========\n"
        )

        print(result)




    # =====================================================
    # VERIFY
    # =====================================================

    def verify(self):

        packages = sorted(
            glob.glob(
                "exports/CRME-PPP-v*.zip"
            )
        )

        if not packages:

            print(
                "\nNo CRME package found.\n"
            )

            return

        package = packages[-1]

        result = self.integrity_engine.verify_zip(
            package,
            "exports/CRME_MANIFEST.json"
        )

        print(
            "\n========== CRME VERIFY ==========\n"
        )

        print(result)


    # =====================================================
    # VERSION
    # =====================================================

    def version(self):

        print(
            "\n========== CRME VERSION ==========\n"
        )


        print(
            self.version_engine.current()
        )


        print(
            "\nHistory:"
        )


        for item in self.version_engine.history():

            print(item)

    # =====================================================
    # REVIEW
    # =====================================================


    def review(self, session_id):

        path = self.review_engine.export_markdown(
            session_id
        )

        print(
            "\n========== CRME SESSION REVIEW ==========\n"
        )

        if path:

            print("Report Created:")
            print(path)

            print("\nStatus: Generated")

        else:

            print("Session not found")


    # =====================================================
    # DASHBOARD
    # =====================================================

    def dashboard(self):

        print("\n========== CRME RESEARCH DASHBOARD ==========\n")

        summary = self.project.summary()

        print("Project:")
        print(" ", summary.get("project"))

        print("\nStatus:")
        print(" ", summary.get("status"))

        print("\nPhase:")
        print(" ", summary.get("phase"))

        print("\nProgress:")
        print(" ", str(summary.get("progress")) + "%")

        print("\nResearch Metrics:")
        print(" Sessions:", summary.get("sessions"))
        print(" Knowledge Nodes:", summary.get("knowledge_nodes"))
        print(" Decisions:", summary.get("decisions"))
        print(" Goals:", summary.get("goals"))
        print(" Artifacts:", summary.get("artifacts"))
        print(" Ledger Entries:", summary.get("ledger_entries"))
        print(" Ideas:", summary.get("ideas"))
        print(" Milestones:", summary.get("milestones"))

        print("\nLatest Package:")

        import glob

        packages = sorted(
            glob.glob("exports/CRME-PPP-v*.zip")
        )

        if packages:
            print(" ", packages[-1])
        else:
            print(" No package found")

        print("\n============================================\n")





    # =====================================================
    # HELP
    # =====================================================

    def help(self):

        print(
"""
CRME CLI 


Usage:

python -m core <command>


Commands:

dashboard
    Show CRME research dashboard


status
    Show project status


start
    Create research session


sessions
    List sessions


memory
    Show memory objects


graph
    Show knowledge graph metrics


query <text>
    Semantic knowledge query


context
    Export CRME context


restore <file>
    Restore CRME context package


insight
    Analyze research intelligence


package
    Create portable CRME package


verify
    Verify package integrity


version
    Show CRME version history


review <session_id>
    Generate session research review

"""
        )



# =====================================================
# MAIN
# =====================================================

def main():

    cli = CRMECLI()


    if len(sys.argv) < 2:

        cli.help()

        return


    command = sys.argv[1]

    if command == "dashboard":
        cli.dashboard()


    elif command == "status":

        cli.status()


    elif command == "start":

        cli.start()


    elif command == "sessions":

        cli.sessions()


    elif command == "memory":

        cli.memory()


    elif command == "graph":

        cli.graph_status()


    elif command == "query":

        if len(sys.argv) < 3:

            print(
                "Usage: python -m core query <text>"
            )

            return


        cli.query(
            " ".join(sys.argv[2:])
        )


    elif command == "context":

        cli.context()


    elif command == "restore":

        if len(sys.argv) < 3:

            print(
                "Usage: python -m core restore <file>"
            )

            return


        cli.restore(
            sys.argv[2]
        )


    elif command == "insight":

        cli.insight()


    elif command == "package":

        cli.package()


    elif command == "verify":

        cli.verify()


    elif command == "version":

        cli.version()


    elif command == "review":

        if len(sys.argv) < 3:

            print(
                "Usage: python -m core review <session_id>"
            )

            return

        cli.review(
            sys.argv[2]
        )


    else:

        cli.help()



if __name__ == "__main__":

    main()
