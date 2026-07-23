import os
import time
from datetime import datetime, timezone


from evaluation.engines.dataset_engine import (
    DatasetEngine
)

from evaluation.benchmark.dataset_loader import (
    DatasetLoader
)

from evaluation.engines.crme_execution_adapter import (
    CRMEExecutionAdapter
)

from evaluation.evaluation_engine import (
    EvaluationEngine
)

from evaluation.experiment.experiment_result import (
    ExperimentResult
)


class ExperimentManager:
    """
    CRME Evaluation Experiment Manager v1.6-dev

    Executes reproducible evaluation experiments
    across multiple registered datasets.
    """

    def __init__(
        self,
        output_dir="evaluation/results/experiments"
    ):

        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

        self.dataset_engine = (
            DatasetEngine()
        )

        self.loader = (
            DatasetLoader()
        )

        self.adapter = (
            CRMEExecutionAdapter()
        )

        self.evaluator = (
            EvaluationEngine()
        )

    # =====================================================
    # RUN EXPERIMENT
    # =====================================================

    def run(
        self,
        datasets
    ):

        experiment_id = (
            "EXP-"
            + datetime.now(
                timezone.utc
            ).strftime(
                "%Y%m%d%H%M%S"
            )
        )

        experiment = ExperimentResult(
            experiment_id=experiment_id,
            datasets=datasets
        )

        experiment.set_status(
            "running"
        )

        started_at = time.perf_counter()

        for dataset_ref in datasets:

            try:

                dataset = (
                    self._resolve_dataset(
                        dataset_ref
                    )
                )

                if dataset is None:

                    continue

                result = (
                    self.evaluator.evaluate(
                        dataset
                    )
                )

                experiment.add_result(
                    result
                )

            except Exception as error:

                experiment.add_result(
                    {
                        "dataset":
                            str(
                                dataset_ref
                            ),

                        "status":
                            "failed",

                        "error":
                            str(
                                error
                            )
                    }
                )

        elapsed = (
            time.perf_counter()
            - started_at
        )

        summary = (
            self._build_summary(
                experiment.data["results"]
            )
        )

        experiment.set_summary(
            summary
        )

        experiment.data[
            "runtime_sec"
        ] = round(
            elapsed,
            6
        )

        experiment.data[
            "finished_at"
        ] = datetime.now(
            timezone.utc
        ).isoformat()

        experiment.set_status(
            "completed"
        )

        path = os.path.join(
            self.output_dir,
            experiment_id
            + ".json"
        )

        experiment.save(
            path
        )

        return experiment

    # =====================================================
    # RESOLVE DATASET
    # =====================================================

    def _resolve_dataset(
        self,
        dataset_ref
    ):

        if isinstance(
            dataset_ref,
            dict
        ):

            return dataset_ref

        return (
            self.dataset_engine
            .registry
            .get(
                dataset_ref
            )
        )

    # =====================================================
    # BUILD SUMMARY
    # =====================================================

    def _build_summary(
        self,
        results
    ):

        metric_names = [
            "mcs",
            "srs",
            "kgq",
            "rrs",
            "ces"
        ]

        summary = {}

        for metric in metric_names:

            values = []

            for result in results:

                metrics = (
                    result.get(
                        "metrics",
                        {}
                    )
                )

                value = metrics.get(
                    metric
                )

                if isinstance(
                    value,
                    (int, float)
                ):

                    values.append(
                        value
                    )

            if values:

                summary[metric] = {
                    "average":
                        round(
                            sum(
                                values
                            )
                            / len(
                                values
                            ),
                            2
                        ),

                    "min":
                        min(
                            values
                        ),

                    "max":
                        max(
                            values
                        ),

                    "count":
                        len(
                            values
                        )
                }

        return summary
