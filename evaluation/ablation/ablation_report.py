import os
import json
from datetime import datetime, timezone


class AblationReport:
    """
    CRME Ablation Study Report Generator v1.0

    Generates:
        - JSON report
        - Markdown report
        - Compact summary

    Input:
        AblationStudy object
    """

    def __init__(
        self,
        output_dir="evaluation/results/ablations"
    ):
        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    # =====================================================
    # NORMALIZATION
    # =====================================================

    def _study_to_dict(self, study):

        if hasattr(study, "to_dict"):
            return study.to_dict()

        if isinstance(study, dict):
            return study

        return {
            "experiment_id": getattr(
                study,
                "experiment_id",
                "unknown"
            ),
            "dataset": getattr(
                study,
                "dataset",
                "unknown"
            ),
            "results": [
                result.to_dict()
                if hasattr(result, "to_dict")
                else result
                for result in getattr(
                    study,
                    "results",
                    []
                )
            ]
        }

    # =====================================================
    # METRIC ANALYSIS
    # =====================================================

    def _analyze_metrics(
        self,
        results
    ):

        full_result = None

        for result in results:

            if result.get(
                "configuration"
            ) == "FULL":

                full_result = result

                break

        if full_result is None:

            return {
                "absolute_degradation": {},
                "relative_degradation": {}
            }

        full_metrics = full_result.get(
            "metrics",
            {}
        )

        absolute_degradation = {}

        relative_degradation = {}

        for result in results:

            configuration = result.get(
                "configuration"
            )

            if configuration == "FULL":

                continue

            metrics = result.get(
                "metrics",
                {}
            )

            absolute_degradation[
                configuration
            ] = {}

            relative_degradation[
                configuration
            ] = {}

            for metric, full_value in full_metrics.items():

                current_value = metrics.get(
                    metric,
                    0
                )

                degradation = (
                    full_value
                    - current_value
                )

                absolute_degradation[
                    configuration
                ][metric] = round(
                    degradation,
                    2
                )

                if full_value == 0:

                    relative_degradation[
                        configuration
                    ][metric] = None

                else:

                    relative_degradation[
                        configuration
                    ][metric] = round(
                        (
                            degradation
                            / full_value
                        ) * 100,
                        2
                    )

        return {
            "absolute_degradation":
                absolute_degradation,

            "relative_degradation":
                relative_degradation
        }

    # =====================================================
    # COMPONENT CONTRIBUTION
    # =====================================================

    def _component_contributions(
        self,
        results
    ):

        contributions = {}

        for result in results:

            configuration = result.get(
                "configuration"
            )

            removed_component = result.get(
                "removed_component"
            )

            if (
                configuration == "FULL"
                or removed_component is None
            ):

                continue

            contributions[
                removed_component
            ] = {

                "configuration":
                    configuration,

                "metric_impact":
                    result.get(
                        "metrics",
                        {}
                    )
            }

        return contributions

    # =====================================================
    # BUILD REPORT
    # =====================================================

    def build_report(
        self,
        study
    ):

        data = self._study_to_dict(
            study
        )

        results = data.get(
            "results",
            []
        )

        analysis = self._analyze_metrics(
            results
        )

        contributions = (
            self._component_contributions(
                results
            )
        )

        report = {

            "report_type":
                "ablation_study",

            "report_version":
                "1.0",

            "experiment_id":
                data.get(
                    "experiment_id"
                ),

            "dataset":
                data.get(
                    "dataset"
                ),

            "configurations":
                len(
                    results
                ),

            "results":
                results,

            "analysis":
                analysis,

            "component_contributions":
                contributions,

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat()
        }

        return report

    # =====================================================
    # MARKDOWN
    # =====================================================

    def to_markdown(
        self,
        report
    ):

        lines = []

        lines.append(
            "# CRME Ablation Study Report"
        )

        lines.append("")

        lines.append(
            f"**Experiment ID:** "
            f"`{report.get('experiment_id')}`"
        )

        lines.append(
            f"**Dataset:** "
            f"`{report.get('dataset')}`"
        )

        lines.append(
            f"**Configurations:** "
            f"`{report.get('configurations')}`"
        )

        lines.append("")

        lines.append(
            "## Configuration Comparison"
        )

        lines.append("")

        results = report.get(
            "results",
            []
        )

        metrics = [
            "mcs",
            "srs",
            "kgq",
            "rrs",
            "ces"
        ]

        header = (
            "| Configuration | "
            + " | ".join(
                metric.upper()
                for metric in metrics
            )
            + " |"
        )

        separator = (
            "|---|"
            + "---|" * len(metrics)
        )

        lines.append(
            header
        )

        lines.append(
            separator
        )

        for result in results:

            configuration = result.get(
                "configuration",
                "UNKNOWN"
            )

            result_metrics = result.get(
                "metrics",
                {}
            )

            values = []

            for metric in metrics:

                value = result_metrics.get(
                    metric,
                    0
                )

                values.append(
                    f"{value:.2f}"
                )

            lines.append(
                "| "
                + configuration
                + " | "
                + " | ".join(
                    values
                )
                + " |"
            )

        lines.append("")

        lines.append(
            "## Absolute Metric Degradation"
        )

        lines.append("")

        absolute = report.get(
            "analysis",
            {}
        ).get(
            "absolute_degradation",
            {}
        )

        for configuration, metrics_data in absolute.items():

            lines.append(
                f"### {configuration}"
            )

            lines.append("")

            for metric, value in metrics_data.items():

                lines.append(
                    f"- **{metric.upper()}**: "
                    f"{value:.2f}"
                )

            lines.append("")

        lines.append(
            "## Relative Performance Degradation"
        )

        lines.append("")

        relative = report.get(
            "analysis",
            {}
        ).get(
            "relative_degradation",
            {}
        )

        for configuration, metrics_data in relative.items():

            lines.append(
                f"### {configuration}"
            )

            lines.append("")

            for metric, value in metrics_data.items():

                if value is None:

                    display = "N/A"

                else:

                    display = f"{value:.2f}%"

                lines.append(
                    f"- **{metric.upper()}**: "
                    f"{display}"
                )

            lines.append("")

        lines.append(
            "## Component Contribution Analysis"
        )

        lines.append("")

        contributions = report.get(
            "component_contributions",
            {}
        )

        for component, data in contributions.items():

            lines.append(
                f"### {component.title()}"
            )

            lines.append("")

            lines.append(
                f"Removed configuration: "
                f"`{data.get('configuration')}`"
            )

            lines.append("")

            for metric, value in data.get(
                "metric_impact",
                {}
            ).items():

                lines.append(
                    f"- **{metric.upper()}**: "
                    f"{value:.2f}"
                )

            lines.append("")

        lines.append(
            "## Interpretation"
        )

        lines.append("")

        lines.append(
            "The ablation study evaluates the contribution "
            "of individual CRME components by comparing "
            "the full architecture against configurations "
            "where one component is removed."
        )

        lines.append("")

        lines.append(
            "The results indicate that each component "
            "contributes differently to the overall "
            "research memory continuity performance."
        )

        lines.append("")

        lines.append(
            "> The full CRME configuration provides the "
            "reference architecture for interpreting "
            "component-level performance degradation."
        )

        return "\n".join(
            lines
        )

    # =====================================================
    # SAVE JSON
    # =====================================================

    def save_json(
        self,
        report
    ):

        experiment_id = report.get(
            "experiment_id",
            "UNKNOWN"
        )

        path = os.path.join(
            self.output_dir,
            experiment_id + ".json"
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False
            )

        return path

    # =====================================================
    # SAVE MARKDOWN
    # =====================================================

    def save_markdown(
        self,
        report
    ):

        experiment_id = report.get(
            "experiment_id",
            "UNKNOWN"
        )

        path = os.path.join(
            self.output_dir,
            experiment_id + ".md"
        )

        markdown = self.to_markdown(
            report
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                markdown
            )

        return path

    # =====================================================
    # SAVE ALL
    # =====================================================

    def save_all(
        self,
        study
    ):

        report = self.build_report(
            study
        )

        json_path = self.save_json(
            report
        )

        markdown_path = self.save_markdown(
            report
        )

        return {

            "json":
                json_path,

            "markdown":
                markdown_path,

            "summary": {

                "experiment_id":
                    report.get(
                        "experiment_id"
                    ),

                "dataset":
                    report.get(
                        "dataset"
                    ),

                "configurations":
                    report.get(
                        "configurations"
                    ),

                "components":
                    list(
                        report.get(
                            "component_contributions",
                            {}
                        ).keys()
                    )
            }
        }

