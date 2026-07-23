import os
from datetime import datetime, timezone

from evaluation.benchmark.benchmark_engine import BenchmarkEngine
from evaluation.metrics.evaluation_metrics import EvaluationMetrics


class EvaluationEngine:
    """
    CRME Evaluation Engine v1.6-dev

    Full evaluation pipeline:

        Dataset
            ↓
        BenchmarkEngine
            ↓
        CRMEExecutionAdapter
            ↓
        EvaluationMetrics
            ↓
        Evaluation Result
    """

    def __init__(
        self,
        benchmark_engine=None,
        metrics_engine=None,
        output_dir="evaluation/results"
    ):

        self.benchmark_engine = (
            benchmark_engine
            or BenchmarkEngine(
                output_dir=output_dir
            )
        )

        self.metrics_engine = (
            metrics_engine
            or EvaluationMetrics()
        )

        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    # =====================================================
    # EVALUATE DATASET
    # =====================================================

    def evaluate(
        self,
        dataset,
        evaluation_id=None
    ):

        if evaluation_id is None:

            evaluation_id = (
                "EVAL-"
                + datetime.now(
                    timezone.utc
                ).strftime(
                    "%Y%m%d%H%M%S"
                )
            )

        started_at = datetime.now(
            timezone.utc
        )

        # -------------------------------------------------
        # 1. RUN REAL BENCHMARK
        # -------------------------------------------------

        benchmark_result = (
            self.benchmark_engine.run(
                dataset
            )
        )

        benchmark_data = (
            benchmark_result.to_dict()
        )

        # -------------------------------------------------
        # 2. PREPARE METRIC INPUT
        # -------------------------------------------------

        metric_input = {

            "memories":
                benchmark_data.get(
                    "memories",
                    0
                ),

            "artifacts":
                benchmark_data.get(
                    "artifacts",
                    0
                ),

            "ledger_entries":
                benchmark_data.get(
                    "ledger_entries",
                    0
                ),

            "retrieved":
                benchmark_data.get(
                    "memories",
                    0
                ),

            "relevant":
                benchmark_data.get(
                    "knowledge_nodes",
                    0
                ),

            "knowledge_nodes":
                benchmark_data.get(
                    "knowledge_nodes",
                    0
                ),

            "relations":
                benchmark_data.get(
                    "relations",
                    0
                ),

            "sessions":
                benchmark_data.get(
                    "sessions",
                    0
                ),

            "decisions":
                benchmark_data.get(
                    "decisions",
                    0
                ),

            "provenance":
                benchmark_data.get(
                    "ledger_entries",
                    0
                )
        }

        # -------------------------------------------------
        # 3. CALCULATE METRICS
        # -------------------------------------------------

        metrics = (
            self.metrics_engine.evaluate(
                metric_input
            )
        )

        finished_at = datetime.now(
            timezone.utc
        )

        # -------------------------------------------------
        # 4. BUILD EVALUATION RESULT
        # -------------------------------------------------

        result = {

            "evaluation_id":
                evaluation_id,

            "dataset":
                dataset.get(
                    "name",
                    "unknown"
                ),

            "benchmark":
                benchmark_data,

            "metrics":
                metrics,

            "started_at":
                started_at.isoformat(),

            "finished_at":
                finished_at.isoformat(),

            "status":
                "completed"
        }

        return result

    # =====================================================
    # SAVE EVALUATION
    # =====================================================

    def save(
        self,
        result
    ):

        evaluation_id = (
            result[
                "evaluation_id"
            ]
        )

        path = os.path.join(
            self.output_dir,
            evaluation_id + ".json"
        )

        import json

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4
            )

        return path

