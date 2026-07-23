import sys
import os


# =====================================================
# CRME CLI
# Unified Runtime Interface
# Uses CRMEBootstrap architecture
# =====================================================


# Add project root
BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.insert(0, BASE_DIR)


from core.bootstrap import CRMEBootstrap
from core.crme_repair_tool import CRMERepairTool



# =====================================================
# INITIALIZE CRME RUNTIME
# =====================================================


runtime = CRMEBootstrap(
    project_id="CRME-001",
    title="CRME Research Core",
    base_path=BASE_DIR
)


crme = runtime.initialize()


repair_tool = CRMERepairTool(BASE_DIR)



# =====================================================
# COMMAND HANDLER
# =====================================================


def main():

    if len(sys.argv) < 2:

        print(
            """
CRME CLI

Commands:

start
state
status
check
repair

Example:

crme start
"""
        )

        return


    cmd = sys.argv[1]



    # -----------------------------------------------
    # START SESSION
    # -----------------------------------------------

    if cmd == "start":

        session_id = crme.start_session(
            project_id="CRME-001"
        )

        print(
            "CRME Session Started:"
        )

        print(session_id)



    # -----------------------------------------------
    # STATUS
    # -----------------------------------------------

    elif cmd == "status":

        print(
            runtime.status()
        )



    # -----------------------------------------------
    # STATE
    # -----------------------------------------------

    elif cmd == "state":

        print(
            runtime.status()
        )



    # -----------------------------------------------
    # HEALTH CHECK
    # -----------------------------------------------

    elif cmd == "check":

        print(
            repair_tool.run_health_check()
        )



    # -----------------------------------------------
    # AUTO REPAIR
    # -----------------------------------------------

    elif cmd == "repair":

        print(
            repair_tool.auto_fix()
        )



    else:

        print(
            "Unknown command:",
            cmd
        )



if __name__ == "__main__":

    main()

