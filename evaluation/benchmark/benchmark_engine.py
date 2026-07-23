import os
import time
from datetime import datetime, timezone

from evaluation.benchmark.benchmark_result import BenchmarkResult
from evaluation.benchmark.dataset_loader import DatasetLoader
from evaluation.engines.crme_execution_adapter import (
    CRMEExecutionAdapter
)


class BenchmarkEngine:
    """
    CRME Evaluation Benchmark Engine v1.6-dev

    Pipeline:

        Dataset
            ↓
        DatasetLoader
            ↓
        CRMEExecutionAdapter
            ↓
        BenchmarkResult
    """

    def __init__(
        self,
        output_dir="evaluation/results",
        loader=None,
        execution_adapter=None
    ):

        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

        self.loader = (
            loader
            or DatasetLoader()
        )

        self.execution_adapter = (
            execution_adapter
            or CRMEExecutionAdapter()
        )

    # =====================================================
    # RUN BENCHMARK
    # =====================================================

    def run(
        self,
        dataset,
        benchmark_id=None
    ):

        if benchmark_id is None:

            benchmark_id = (
                "BENCH-"
                + datetime.now(
                    timezone.utc
                ).strftime(
                    "%Y%m%d%H%M%S"
                )
            )

        started_at = datetime.now(
            timezone.utc
        )

        result = BenchmarkResult(

            benchmark_id,

            dataset.get(
                "name",
                "unknown"
            ),

            dataset.get(
                "source",
                "unknown"
            )
        )

        start_time = time.perf_counter()

        # -------------------------------------------------
        # LOAD DATASET
        # -------------------------------------------------

        loaded_dataset = self.loader.load(
            dataset
        )

        # -------------------------------------------------
        # EXECUTE CRME
        # -------------------------------------------------

        execution = (
            self.execution_adapter.execute(
                loaded_dataset
            )
        )

        runtime = (
            time.perf_counter()
            - start_time
        )

        # -------------------------------------------------
        # UPDATE BENCHMARK RESULT
        # -------------------------------------------------

        result.update(

            runtime_sec=round(
                runtime,
                6
            ),

            samples=loaded_dataset.get(
                "sample_count",
                0
            ),

            processed_objects=execution.get(
                "processed_objects",
                0
            ),

            knowledge_nodes=execution.get(
                "knowledge_nodes",
                0
            ),

            relations=execution.get(
                "relations",
                0
            ),

            sessions=execution.get(
                "sessions",
                0
            ),

            memories=execution.get(
                "memories",
                0
            ),

            decisions=execution.get(
                "decisions",
                0
            ),

            goals=execution.get(
                "goals",
                0
            ),

            artifacts=execution.get(
                "artifacts",
                0
            ),

            ledger_entries=execution.get(
                "ledger_entries",
                0
            ),

            metadata={

                "engine":
                    "BenchmarkEngine",

                "version":
                    "1.6-dev",

                "dataset_type":
                    loaded_dataset.get(
                        "dataset_type",
                        "unknown"
                    ),

                "total_records":
                    loaded_dataset.get(
                        "total_records",
                        0
                    ),

                "execution_version":
                    execution.get(
                        "execution_version"
                    ),

                "started_at":
                    started_at.isoformat(),

                "finished_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat()
            }
        )

        return result

    # =====================================================
    # SAVE RESULT
    # =====================================================

    def save_result(
        self,
        result
    ):

        filename = (
            result.data[
                "benchmark_id"
            ]
            + ".json"
        )

        path = os.path.join(
            self.output_dir,
            filename
        )

        return result.save(
            path
        )

