class StatisticalAnalysisResult:
    """
    Statistical analysis result for CRME experiments and ablation studies.
    """

    def __init__(
        self,
        analysis_id,
        source_type,
        source_id,
        dataset,
        metrics,
        component_analysis=None,
        metadata=None
    ):
        self.analysis_id = analysis_id
        self.source_type = source_type
        self.source_id = source_id
        self.dataset = dataset
        self.metrics = metrics
        self.component_analysis = (
            component_analysis
            or {}
        )
        self.metadata = (
            metadata
            or {}
        )

    def to_dict(self):
        return {
            "analysis_id": self.analysis_id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "dataset": self.dataset,
            "metrics": self.metrics,
            "component_analysis": self.component_analysis,
            "metadata": self.metadata
        }

    def summary(self):
        return {
            "analysis_id": self.analysis_id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "dataset": self.dataset,
            "metrics": list(
                self.metrics.keys()
            ),
            "components": list(
                self.component_analysis.keys()
            )
        }
