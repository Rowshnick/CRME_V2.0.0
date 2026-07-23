import json
import os
from datetime import datetime, timezone


class ComparisonReport:
    """
    CRME Comparison Report Generator v1.0

    Converts ComparisonEngine output into:
        - JSON report
        - Markdown report
        - Summary dictionary
    """

    def __init__(
        self,
        output_dir="evaluation/results/comparisons"
    ):

        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    # =====================================================
    # SAVE ALL
    # =====================================================

    def save_all(
        self,
        comparison
    ):

        comparison_id = comparison[
            "comparison_id"
        ]

        json_path = os.path.join(
            self.output_dir,
            comparison_id + ".json"
        )

        markdown_path = os.path.join(
            self.output_dir,
            comparison_id + ".md"
        )

        with open(
            json_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                comparison,
                file,
                indent=4,
                ensure_ascii=False
            )

        markdown = self.to_markdown(
            comparison
        )

        with open(
            markdown_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                markdown
            )

        return {

            "json":
                json_path,

            "markdown":
                markdown_path,

            "summary":
                self.summary(
                    comparison
                )
        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
        comparison
    ):

        return {

            "comparison_id":
                comparison.get(
                    "comparison_id"
                ),

            "experiment_id":
                comparison.get(
                    "experiment_id"
                ),

            "datasets":
                comparison.get(
                    "datasets",
                    0
                ),

            "metrics":
                comparison.get(
                    "metrics",
                    []
                ),

            "best_dataset":
                comparison.get(
                    "best_dataset",
                    {}
                ),

            "differences":
                comparison.get(
                    "differences",
                    {}
                ),

            "relative_improvement":
                comparison.get(
                    "relative_improvement",
                    {}
                ),

            "status":
                comparison.get(
                    "status",
                    "unknown"
                )
        }

    # =====================================================
    # MARKDOWN REPORT
    # =====================================================

    def to_markdown(
        self,
        comparison
    ):

        comparison_id = comparison.get(
            "comparison_id",
            "unknown"
        )

        experiment_id = comparison.get(
            "experiment_id",
            "unknown"
        )

        datasets = comparison.get(
            "datasets",
            0
        )

        metrics = comparison.get(
            "metrics",
            []
        )

        rankings = comparison.get(
            "rankings",
            {}
        )

        best_dataset = comparison.get(
            "best_dataset",
            {}
        )

        differences = comparison.get(
            "differences",
            {}
        )

        relative_improvement = comparison.get(
            "relative_improvement",
            {}
        )

        created_at = comparison.get(
            "created_at",
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        dataset_names = []

        for metric in metrics:

            for item in rankings.get(
                metric,
                []
            ):

                dataset = item.get(
                    "dataset"
                )

                if (
                    dataset
                    and dataset
                    not in dataset_names
                ):

                    dataset_names.append(
                        dataset
                    )

        lines = []

        lines.append(
            "# CRME Comparison Report"
        )

        lines.append("")

        lines.append(
            f"**Comparison ID:** `{comparison_id}`"
        )

        lines.append(
            f"**Experiment ID:** `{experiment_id}`"
        )

        lines.append(
            f"**Datasets:** `{datasets}`"
        )

        lines.append(
            f"**Created:** `{created_at}`"
        )

        lines.append("")

        lines.append(
            "## Metric Performance"
        )

        lines.append("")

        header = (
            "| Metric | "
            + " | ".join(
                dataset_names
            )
            + " |"
        )

        separator = (
            "|---|"
            + "|".join(
                ["---"]
                * len(
                    dataset_names
                )
            )
            + "|"
        )

        lines.append(
            header
        )

        lines.append(
            separator
        )

        for metric in metrics:

            values = {}

            for item in rankings.get(
                metric,
                []
            ):

                values[
                    item["dataset"]
                ] = item["value"]

            row = [

                metric.upper()

            ]

            for dataset in dataset_names:

                value = values.get(
                    dataset,
                    0.0
                )

                row.append(
                    f"{value:.2f}"
                )

            lines.append(
                "| "
                + " | ".join(
                    row
                )
                + " |"
            )

        lines.append("")

        lines.append(
            "## Best Dataset per Metric"
        )

        lines.append("")

        for metric in metrics:

            best = best_dataset.get(
                metric
            )

            if best:

                lines.append(
                    f"- **{metric.upper()}**: "
                    f"{best['dataset']} "
                    f"({best['value']:.2f})"
                )

        lines.append("")

        lines.append(
            "## Absolute Differences"
        )

        lines.append("")

        for metric in metrics:

            difference = differences.get(
                metric,
                0.0
            )

            lines.append(
                f"- **{metric.upper()}**: "
                f"{difference:.2f}"
            )

        lines.append("")

        lines.append(
            "## Relative Improvement"
        )

        lines.append("")

        for metric in metrics:

            improvement = relative_improvement.get(
                metric
            )

            if improvement is None:

                lines.append(
                    f"- **{metric.upper()}**: "
                    "N/A"
                )

            else:

                lines.append(
                    f"- **{metric.upper()}**: "
                    f"{improvement:.2f}%"
                )

        lines.append("")

        lines.append(
            "## Interpretation"
        )

        lines.append("")

        lines.append(
            "The comparison evaluates CRME performance "
            "across the registered datasets using the "
            "MCS, SRS, KGQ, RRS, and CES metrics."
        )

        lines.append("")

        lines.append(
            "The best-performing dataset for each metric "
            "is identified based on the highest metric value."
        )

        lines.append("")

        lines.append(
            "> Note: Dataset comparisons should be "
            "interpreted in the context of dataset structure "
            "and semantic suitability for the CRME architecture."
        )

        lines.append("")

        return "\n".join(
            lines
        )

