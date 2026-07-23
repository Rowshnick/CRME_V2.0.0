from datetime import datetime

from evaluation.benchmark.benchmark_engine import BenchmarkEngine
from evaluation.metrics.evaluation_metrics import EvaluationMetrics


class EvaluationEngine:
    """
    CRME Evaluation Engine

    Pipeline:

        Dataset
            ↓
        BenchmarkEngine
            ↓
        EvaluationMetrics
            ↓
        Evaluation Result
    """

    def __init__(self):

        self.benchmark_engine = BenchmarkEngine()

        self.metrics_engine = EvaluationMetrics()

    # =========================================================
    # RUN EVALUATION
    # =========================================================

    def evaluate(self, dataset):

        started_at = datetime.utcnow()

        # -----------------------------------------------------
        # 1. Run benchmark
        # -----------------------------------------------------

        benchmark_result = self.benchmark_engine.run(dataset)

        # -----------------------------------------------------
        # 2. Extract real benchmark data
        # -----------------------------------------------------

        benchmark_data = benchmark_result.to_dict()

        # -----------------------------------------------------
        # 3. Map benchmark metrics to EvaluationMetrics
        # -----------------------------------------------------

        metrics_input = {

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

                    "memories",

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

        # -----------------------------------------------------
        # 4. Calculate metrics
        # -----------------------------------------------------

        metrics = self.metrics_engine.evaluate(

            metrics_input

        )

        # -----------------------------------------------------
        # 5. Store CES in benchmark result
        # -----------------------------------------------------

        benchmark_result.update(

            ces_score=

                metrics.get(

                    "ces",

                    0.0

                )

        )

        # -----------------------------------------------------
        # 6. Final evaluation result
        # -----------------------------------------------------

        finished_at = datetime.utcnow()

        return {

            "evaluation_id":

                "EVAL-"

                +

                datetime.utcnow().strftime(

                    "%Y%m%d%H%M%S"

                ),

            "dataset":

                benchmark_data.get(

                    "dataset",

                    "unknown"

                ),

            "benchmark":

                benchmark_result.to_dict(),

            "metrics":

                metrics,

            "started_at":

                started_at.isoformat(),

            "finished_at":

                finished_at.isoformat(),

            "status":

                "completed"

        }

