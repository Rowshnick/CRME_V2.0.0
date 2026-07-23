import time
from datetime import datetime, timezone


class CRMEExecutionAdapter:
    """
    CRME Evaluation Execution Adapter v1.6-dev

    Converts different dataset formats into a
    unified CRME execution representation.

    Supported dataset types:

    1. Structured Research Benchmark
       - objects
       - relations
       - sessions
       - decisions
       - artifacts

    2. Tabular / CSV
       - records
       - samples

    The adapter is isolated from the Stable Core.
    """

    def __init__(self):

        self.version = "1.6-dev"

    # =====================================================
    # EXECUTE DATASET
    # =====================================================

    def execute(self, loaded_dataset):

        started_at = datetime.now(
            timezone.utc
        )

        start_time = time.perf_counter()

        # -------------------------------------------------
        # Extract dataset payload
        # -------------------------------------------------

        data = loaded_dataset.get(
            "data",
            {}
        )

        # -------------------------------------------------
        # Case 1: Structured Dataset
        # -------------------------------------------------

        if isinstance(data, dict):

            objects = data.get(
                "objects",
                []
            )

            relations = data.get(
                "relations",
                []
            )

            sessions = data.get(
                "sessions",
                []
            )

            decisions = data.get(
                "decisions",
                []
            )

            artifacts = data.get(
                "artifacts",
                []
            )

            records = []

        # -------------------------------------------------
        # Case 2: Tabular Dataset
        # -------------------------------------------------

        elif isinstance(data, list):

            records = data

            objects = records

            relations = []

            sessions = []

            decisions = []

            artifacts = []

        # -------------------------------------------------
        # Unsupported Dataset Payload
        # -------------------------------------------------

        else:

            raise TypeError(
                "Unsupported dataset payload type: "
                + type(data).__name__
            )

        # -------------------------------------------------
        # CRME execution representation
        # -------------------------------------------------

        knowledge_nodes = len(
            objects
        )

        processed_relations = len(
            relations
        )

        processed_sessions = len(
            sessions
        )

        processed_decisions = len(
            decisions
        )

        processed_artifacts = len(
            artifacts
        )

        # -------------------------------------------------
        # Research Memory Units
        # -------------------------------------------------

        memories = (
            knowledge_nodes
            + processed_decisions
        )

        # -------------------------------------------------
        # Ledger Entries
        # -------------------------------------------------

        ledger_entries = (
            processed_decisions
        )

        # -------------------------------------------------
        # Goals
        # -------------------------------------------------

        goals = 0

        # -------------------------------------------------
        # Runtime
        # -------------------------------------------------

        runtime = (
            time.perf_counter()
            - start_time
        )

        finished_at = datetime.now(
            timezone.utc
        )

        total_processed = (
            knowledge_nodes
            + processed_relations
            + processed_sessions
            + processed_decisions
            + processed_artifacts
        )

        # -------------------------------------------------
        # Execution Result
        # -------------------------------------------------

        return {

            "execution_version":
                self.version,

            "started_at":
                started_at.isoformat(),

            "finished_at":
                finished_at.isoformat(),

            "runtime_sec":
                round(
                    runtime,
                    6
                ),

            "knowledge_nodes":
                knowledge_nodes,

            "relations":
                processed_relations,

            "sessions":
                processed_sessions,

            "memories":
                memories,

            "decisions":
                processed_decisions,

            "goals":
                goals,

            "artifacts":
                processed_artifacts,

            "ledger_entries":
                ledger_entries,

            "processed_objects":
                knowledge_nodes,

            "records":
                len(records),

            "total_processed":
                total_processed
        }

