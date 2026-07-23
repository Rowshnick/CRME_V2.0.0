import json
import os
from datetime import datetime, timezone
from statistics import mean, stdev


class StatisticalAnalysisEngine:
    """
    CRME Statistical Analysis Engine v1.0

    Supports:
        - Ablation analysis
        - Experiment analysis
        - Mean / standard deviation
        - Absolute degradation
        - Relative degradation
        - Component ranking
        - JSON / Markdown reports
    """

    def __init__(
        self,
        output_dir="evaluation/results/statistics"
    ):
        self.version = "1.0"

        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    # =====================================================
    # BASIC STATISTICS
    # =====================================================

    def _statistics(
        self,
        values
    ):
        if not values:
            return {
                "mean": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "count": 0
            }

        if len(values) > 1:
            std_value = stdev(
                values
            )
        else:
            std_value = 0.0

        return {
            "mean": round(
                mean(values),
                4
            ),
            "std": round(
                std_value,
                4
            ),
            "min": round(
                min(values),
                4
            ),
            "max": round(
                max(values),
                4
            ),
            "count": len(values)
        }

    # =====================================================
    # ABLATION ANALYSIS
    # =====================================================

    def analyze_ablation(
        self,
        ablation_study
    ):
        analysis_id = (
            "STAT-"
            + datetime.now(
                timezone.utc
            ).strftime(
                "%Y%m%d%H%M%S"
            )
        )

        results = (
            ablation_study.results
        )

        if not results:
            raise ValueError(
                "Ablation study contains no results"
            )

        full_result = None

        for result in results:

            if (
                result.configuration
                == "FULL"
            ):
                full_result = result
                break

        if full_result is None:
            raise ValueError(
                "FULL configuration not found"
            )

        baseline_metrics = (
            full_result.metrics
        )

        component_analysis = {}

        for result in results:

            if (
                result.configuration
                == "FULL"
            ):
                continue

            component = (
                result.removed_component
            )

            if not component:
                continue

            metric_analysis = {}

            total_degradation = 0.0

            for metric, baseline in (
                baseline_metrics.items()
            ):

                ablated = (
                    result.metrics.get(
                        metric,
                        0.0
                    )
                )

                absolute_degradation = (
                    baseline
                    - ablated
                )

                if baseline != 0:

                    relative_degradation = (
                        absolute_degradation
                        / baseline
                    ) * 100

                else:

                    relative_degradation = None

                metric_analysis[
                    metric
                ] = {
                    "baseline": round(
                        baseline,
                        4
                    ),
                    "ablated": round(
                        ablated,
                        4
                    ),
                    "absolute_degradation": round(
                        absolute_degradation,
                        4
                    ),
                    "relative_degradation": (
                        round(
                            relative_degradation,
                            4
                        )
                        if relative_degradation
                        is not None
                        else None
                    )
                }

                total_degradation += (
                    max(
                        absolute_degradation,
                        0
                    )
                )

            component_analysis[
                component
            ] = {
                "removed_configuration": (
                    result.configuration
                ),
                "metrics": metric_analysis,
                "total_degradation": round(
                    total_degradation,
                    4
                )
            }

        ranked_components = sorted(
            component_analysis.items(),
            key=lambda item: item[1][
                "total_degradation"
            ],
            reverse=True
        )

        for rank, (
            component,
            analysis
        ) in enumerate(
            ranked_components,
            start=1
        ):

            component_analysis[
                component
            ][
                "contribution_rank"
            ] = rank

        metrics = {
            "baseline": baseline_metrics,
            "component_statistics": {
                metric: self._statistics(
                    [
                        result.metrics.get(
                            metric,
                            0.0
                        )
                        for result in results
                    ]
                )
                for metric in baseline_metrics
            }
        }

        dataset = (
            full_result.dataset
        )

        return {
            "analysis_id": analysis_id,
            "source_type": "ablation",
            "source_id": getattr(
                ablation_study,
                "experiment_id",
                None
            ),
            "dataset": dataset,
            "engine_version": self.version,
            "metrics": metrics,
            "component_analysis": (
                component_analysis
            ),
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": "completed"
        }

    # =====================================================
    # SAVE JSON
    # =====================================================

    def save_json(
        self,
        result
    ):
        path = os.path.join(
            self.output_dir,
            result[
                "analysis_id"
            ]
            + ".json"
        )

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

    # =====================================================
    # SAVE MARKDOWN
    # =====================================================

    def save_markdown(
        self,
        result
    ):
        path = os.path.join(
            self.output_dir,
            result[
                "analysis_id"
            ]
            + ".md"
        )

        lines = []

        lines.append(
            "# CRME Statistical Analysis Report\n"
        )

        lines.append(
            f"**Analysis ID:** `{result['analysis_id']}`  \n"
        )

        lines.append(
            f"**Source:** `{result['source_type']}`  \n"
        )

        lines.append(
            f"**Dataset:** `{result['dataset']}`  \n"
        )

        lines.append(
            f"**Engine Version:** `{result['engine_version']}`  \n"
        )

        lines.append(
            "## Baseline Metrics\n"
        )

        lines.append(
            "| Metric | Baseline |\n"
            "|---|---|\n"
        )

        for metric, value in (
            result[
                "metrics"
            ][
                "baseline"
            ].items()
        ):

            lines.append(
                f"| {metric.upper()} | "
                f"{value:.2f} |\n"
            )

        lines.append(
            "\n## Component Contribution Ranking\n"
        )

        lines.append(
            "| Rank | Component | Total Degradation |\n"
            "|---|---|---|\n"
        )

        ranked = sorted(
            result[
                "component_analysis"
            ].items(),
            key=lambda item: item[1][
                "contribution_rank"
            ]
        )

        for component, analysis in ranked:

            lines.append(
                f"| "
                f"{analysis['contribution_rank']} | "
                f"{component} | "
                f"{analysis['total_degradation']:.2f} |\n"
            )

        lines.append(
            "\n## Detailed Component Analysis\n"
        )

        for component, analysis in ranked:

            lines.append(
                f"\n### {component.title()}\n"
            )

            lines.append(
                "| Metric | Baseline | Ablated | "
                "Absolute Degradation | Relative Degradation |\n"
                "|---|---:|---:|---:|---:|\n"
            )

            for metric, values in (
                analysis[
                    "metrics"
                ].items()
            ):

                relative = (
                    "N/A"
                    if values[
                        "relative_degradation"
                    ] is None
                    else f"{values['relative_degradation']:.2f}%"
                )

                lines.append(
                    f"| {metric.upper()} | "
                    f"{values['baseline']:.2f} | "
                    f"{values['ablated']:.2f} | "
                    f"{values['absolute_degradation']:.2f} | "
                    f"{relative} |\n"
                )

        lines.append(
            "\n## Interpretation\n"
        )

        if ranked:

            top_component = ranked[0][0]

            lines.append(
                "The statistical analysis indicates that "
                f"`{top_component}` has the highest aggregate "
                "contribution to the measured CRME performance "
                "among the evaluated components.\n"
            )

        lines.append(
            "\n> The analysis is based on the observed "
            "degradation between the full CRME configuration "
            "and each corresponding ablated configuration.\n"
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.writelines(
                lines
            )

        return path

    # =====================================================
    # SAVE ALL
    # =====================================================

    def save_all(
        self,
        result
    ):
        return {
            "json": self.save_json(
                result
            ),
            "markdown": self.save_markdown(
                result
            ),
            "summary": {
                "analysis_id": result[
                    "analysis_id"
                ],
                "source_type": result[
                    "source_type"
                ],
                "dataset": result[
                    "dataset"
                ],
                "components": len(
                    result[
                        "component_analysis"
                    ]
                ),
                "status": result[
                    "status"
                ]
            }
        }
