from datetime import datetime, timezone


class ComparisonEngine:
    """
    CRME Comparison Engine v1.0

    Compares evaluation results produced by an Experiment.

    Responsibilities:
        - rank datasets by metric
        - identify best dataset per metric
        - calculate metric differences
        - calculate relative improvement
        - generate a comparison summary
    """

    METRICS = [
        "mcs",
        "srs",
        "kgq",
        "rrs",
        "ces",
    ]

    def __init__(self):

        self.version = "1.0"

    # =====================================================
    # COMPARE EXPERIMENT
    # =====================================================

    def compare(
        self,
        experiment
    ):

        experiment_data = (
            experiment.to_dict()
        )

        experiment_id = (
            experiment_data.get(
                "experiment_id",
                "unknown"
            )
        )

        results = (
            experiment_data.get(
                "results",
                []
            )
        )

        valid_results = []

        for result in results:

            if (
                result.get(
                    "status"
                )
                != "completed"
            ):

                continue

            metrics = result.get(
                "metrics",
                {}
            )

            dataset = result.get(
                "dataset",
                "unknown"
            )

            valid_results.append(
                {
                    "dataset":
                        dataset,

                    "metrics":
                        metrics
                }
            )

        best_dataset = {}

        rankings = {}

        differences = {}

        relative_improvement = {}

        for metric in self.METRICS:

            metric_values = []

            for result in valid_results:

                value = result[
                    "metrics"
                ].get(
                    metric,
                    0.0
                )

                metric_values.append(
                    {
                        "dataset":
                            result[
                                "dataset"
                            ],

                        "value":
                            float(
                                value
                            )
                    }
                )

            metric_values.sort(
                key=lambda item:
                    item["value"],

                reverse=True
            )

            rankings[
                metric
            ] = metric_values

            if metric_values:

                best = (
                    metric_values[0]
                )

                best_dataset[
                    metric
                ] = best

                if len(
                    metric_values
                ) > 1:

                    best_value = (
                        metric_values[0][
                            "value"
                        ]
                    )

                    second_value = (
                        metric_values[1][
                            "value"
                        ]
                    )

                    difference = (
                        best_value
                        - second_value
                    )

                    differences[
                        metric
                    ] = round(
                        difference,
                        2
                    )

                    if second_value != 0:

                        improvement = (
                            (
                                best_value
                                - second_value
                            )
                            / second_value
                        ) * 100

                        relative_improvement[
                            metric
                        ] = round(
                            improvement,
                            2
                        )

                    else:

                        relative_improvement[
                            metric
                        ] = None

                else:

                    differences[
                        metric
                    ] = 0.0

                    relative_improvement[
                        metric
                    ] = None

        return {

            "comparison_id":
                self._generate_id(),

            "experiment_id":
                experiment_id,

            "engine_version":
                self.version,

            "datasets":
                len(
                    valid_results
                ),

            "metrics":
                self.METRICS,

            "best_dataset":
                best_dataset,

            "rankings":
                rankings,

            "differences":
                differences,

            "relative_improvement":
                relative_improvement,

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "status":
                "completed"
        }

    # =====================================================
    # ID GENERATION
    # =====================================================

    def _generate_id(
        self
    ):

        return (
            "CMP-"
            + datetime.now(
                timezone.utc
            ).strftime(
                "%Y%m%d%H%M%S"
            )
        )

