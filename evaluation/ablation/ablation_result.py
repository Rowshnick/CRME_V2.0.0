from datetime import datetime, timezone


class AblationResult:
    """
    Result container for one ablation configuration.
    """

    def __init__(
        self,
        experiment_id,
        configuration,
        dataset,
        metrics,
        execution=None,
        removed_component=None
    ):
        self.experiment_id = experiment_id
        self.configuration = configuration
        self.dataset = dataset
        self.metrics = metrics
        self.execution = execution or {}
        self.removed_component = removed_component

        self.created_at = datetime.now(
            timezone.utc
        ).isoformat()

    def to_dict(self):
        return {
            "experiment_id": self.experiment_id,
            "configuration": self.configuration,
            "dataset": self.dataset,
            "removed_component": self.removed_component,
            "metrics": self.metrics,
            "execution": self.execution,
            "created_at": self.created_at
        }

    def summary(self):
        return {
            "configuration": self.configuration,
            "dataset": self.dataset,
            "removed_component": self.removed_component,
            "metrics": self.metrics
        }

