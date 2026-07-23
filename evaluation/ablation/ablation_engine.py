import copy
from datetime import datetime, timezone

from evaluation.engines.dataset_engine import DatasetEngine
from evaluation.benchmark.dataset_loader import DatasetLoader
from evaluation.engines.crme_execution_adapter import (
    CRMEExecutionAdapter
)
from evaluation.metrics.evaluation_metrics import EvaluationMetrics

from evaluation.ablation.ablation_result import (
    AblationResult
)


class AblationEngine:
    """
    CRME Ablation Study Engine v1.0

    Evaluates the contribution of individual CRME
    structural components by controlled removal.

    Baseline:
        Full CRME

    Ablation configurations:
        - WITHOUT_RELATIONS
        - WITHOUT_SESSIONS
        - WITHOUT_DECISIONS
        - WITHOUT_ARTIFACTS
    """

    CONFIGURATIONS = {
        "FULL": None,
        "WITHOUT_RELATIONS": "relations",
        "WITHOUT_SESSIONS": "sessions",
        "WITHOUT_DECISIONS": "decisions",
        "WITHOUT_ARTIFACTS": "artifacts"
    }

    def __init__(
        self,
        dataset_engine=None,
        loader=None,
        adapter=None,
        metrics_engine=None
    ):

        self.dataset_engine = (
            dataset_engine
            or DatasetEngine()
        )

        self.loader = (
            loader
            or DatasetLoader()
        )

        self.adapter = (
            adapter
            or CRMEExecutionAdapter()
        )

        self.metrics_engine = (
            metrics_engine
            or EvaluationMetrics()
        )

    # =====================================================
    # LOAD DATASET
    # =====================================================

    def _load_dataset(
        self,
        dataset_id
    ):

        dataset = (
            self.dataset_engine.registry.get(
                dataset_id
            )
        )

        if dataset is None:
            raise ValueError(
                f"Dataset not found: {dataset_id}"
            )

        return self.loader.load(
            dataset
        )

    # =====================================================
    # APPLY ABLATION
    # =====================================================

    def _apply_ablation(
        self,
        loaded_dataset,
        component
    ):

        data = copy.deepcopy(
            loaded_dataset
        )

        if component is None:
            return data

        if component in data.get(
            "data",
            {}
        ):

            data["data"][
                component
            ] = []

        return data

    # =====================================================
    # CALCULATE METRICS
    # =====================================================

    def _calculate_metrics(
        self,
        execution
    ):

        metric_input = {

            "memories":
                execution.get(
                    "memories",
                    0
                ),

            "artifacts":
                execution.get(
                    "artifacts",
                    0
                ),

            "ledger_entries":
                execution.get(
                    "ledger_entries",
                    0
                ),

            "retrieved":
                execution.get(
                    "memories",
                    0
                ),

            "relevant":
                execution.get(
                    "knowledge_nodes",
                    0
                ),

            "knowledge_nodes":
                execution.get(
                    "knowledge_nodes",
                    0
                ),

            "relations":
                execution.get(
                    "relations",
                    0
                ),

            "sessions":
                execution.get(
                    "sessions",
                    0
                ),

            "decisions":
                execution.get(
                    "decisions",
                    0
                ),

            "provenance":
                execution.get(
                    "ledger_entries",
                    0
                )
        }

        return self.metrics_engine.evaluate(
            metric_input
        )

    # =====================================================
    # RUN ABLATION STUDY
    # =====================================================

    def run(
        self,
        dataset_id
    ):

        experiment_id = (
            "ABL-"
            + datetime.now(
                timezone.utc
            ).strftime(
                "%Y%m%d%H%M%S"
            )
        )

        loaded_dataset = (
            self._load_dataset(
                dataset_id
            )
        )

        results = []

        for configuration, component in (
            self.CONFIGURATIONS.items()
        ):

            ablated_dataset = (
                self._apply_ablation(
                    loaded_dataset,
                    component
                )
            )

            execution = (
                self.adapter.execute(
                    ablated_dataset
                )
            )

            metrics = (
                self._calculate_metrics(
                    execution
                )
            )

            result = AblationResult(
                experiment_id=experiment_id,
                configuration=configuration,
                dataset=loaded_dataset.get(
                    "name",
                    dataset_id
                ),
                metrics=metrics,
                execution=execution,
                removed_component=component
            )

            results.append(
                result
            )

        return AblationStudy(
            experiment_id=experiment_id,
            dataset=dataset_id,
            results=results
        )


class AblationStudy:

    def __init__(
        self,
        experiment_id,
        dataset,
        results
    ):

        self.experiment_id = experiment_id
        self.dataset = dataset
        self.results = results

        self.created_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

    def to_dict(self):

        return {
            "experiment_id":
                self.experiment_id,

            "dataset":
                self.dataset,

            "created_at":
                self.created_at,

            "results":
                [
                    result.to_dict()
                    for result in self.results
                ]
        }

    def summary(self):

        return {
            "experiment_id":
                self.experiment_id,

            "dataset":
                self.dataset,

            "configurations":
                len(
                    self.results
                ),

            "status":
                "completed"
        }
