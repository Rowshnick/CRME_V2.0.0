import json
import os
from datetime import datetime, timezone


class EvaluationResultsAggregator:
    """
    Aggregate CRME evaluation artifacts into a canonical,
    paper-ready evidence package.
    """

    def __init__(self, output_dir="evaluation/results/final"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _load_json(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _aggregate_experiment(self, comparison):
        metrics = comparison.get("metrics", [])

        return {
            "experiment_id": comparison.get("experiment_id"),
            "dataset_count": comparison.get("datasets", 0),
            "metric_count": len(metrics),
            "metrics": metrics,
            "status": "completed",
        }

    def _aggregate_comparison(self, comparison):
        return {
            "comparison_id": comparison.get("comparison_id"),
            "experiment_id": comparison.get("experiment_id"),
            "datasets": comparison.get("datasets", 0),
            "metrics": comparison.get("metrics", []),
            "best_dataset": comparison.get("best_dataset", {}),
            "relative_improvement": comparison.get(
                "relative_improvement", {}
            ),
            "status": "completed",
        }

    def _aggregate_ablation(self, ablation, statistics):
        component_analysis = statistics.get(
            "component_analysis", {}
        )

        components = list(component_analysis.keys())

        configuration_count = ablation.get(
            "configurations",
            ablation.get("configuration_count", 0),
        )

        return {
            "experiment_id": ablation.get("experiment_id"),
            "dataset": ablation.get("dataset"),
            "configuration_count": configuration_count,
            "component_count": len(components),
            "components": components,
            "status": "completed",
        }

    def _aggregate_statistics(self, statistics):
        ranking = []

        for component, data in statistics.get(
            "component_analysis", {}
        ).items():

            ranking.append(
                {
                    "component": component,
                    "total_degradation": data.get(
                        "total_degradation", 0
                    ),
                    "contribution_rank": data.get(
                        "contribution_rank"
                    ),
                }
            )

        ranking.sort(
            key=lambda item: item.get(
                "contribution_rank", 999
            )
        )

        return {
            "analysis_id": statistics.get("analysis_id"),
            "dataset": statistics.get("dataset"),
            "baseline_metrics": statistics.get(
                "metrics", {}
            ).get("baseline", {}),
            "component_ranking": ranking,
            "status": "completed",
        }

    def _write_markdown(self, summary, path):
        lines = []

        lines.append("# CRME Evaluation Evidence Package")
        lines.append("")
        lines.append(
            f"**Generated:** "
            f"{summary['created_at']}"
        )
        lines.append("")

        lines.append("## Evaluation Pipeline")
        lines.append("")
        lines.append(
            "experiment → comparison → "
            "ablation → statistics"
        )
        lines.append("")

        experiment = summary.get("experiment", {})
        comparison = summary.get("comparison", {})
        ablation = summary.get("ablation", {})
        statistics = summary.get("statistics", {})

        lines.append("## Experiment")
        lines.append("")
        lines.append(
            f"- Experiment ID: "
            f"`{experiment.get('experiment_id')}`"
        )
        lines.append(
            f"- Datasets: "
            f"{experiment.get('dataset_count', 0)}"
        )
        lines.append(
            f"- Metrics: "
            f"{experiment.get('metric_count', 0)}"
        )
        lines.append("- Status: `completed`")
        lines.append("")

        lines.append("## Dataset Comparison")
        lines.append("")
        lines.append(
            f"- Comparison ID: "
            f"`{comparison.get('comparison_id')}`"
        )
        lines.append(
            f"- Datasets: "
            f"{comparison.get('datasets', 0)}"
        )
        lines.append("")

        lines.append("### Best Dataset by Metric")
        lines.append("")

        for metric, result in comparison.get(
            "best_dataset", {}
        ).items():
            lines.append(
                f"- **{metric.upper()}**: "
                f"{result.get('dataset')} "
                f"({result.get('value')})"
            )

        lines.append("")
        lines.append("## Ablation Study")
        lines.append("")
        lines.append(
            f"- Experiment ID: "
            f"`{ablation.get('experiment_id')}`"
        )
        lines.append(
            f"- Dataset: "
            f"`{ablation.get('dataset')}`"
        )
        lines.append(
            f"- Configurations: "
            f"{ablation.get('configuration_count', 0)}"
        )
        lines.append(
            f"- Components: "
            f"{ablation.get('component_count', 0)}"
        )
        lines.append("")

        lines.append("## Statistical Evaluation")
        lines.append("")
        lines.append("### Baseline Metrics")
        lines.append("")

        for metric, value in statistics.get(
            "baseline_metrics", {}
        ).items():
            lines.append(
                f"- **{metric.upper()}**: {value}"
            )

        lines.append("")
        lines.append(
            "### Component Contribution Ranking"
        )
        lines.append("")

        for item in statistics.get(
            "component_ranking", []
        ):
            lines.append(
                f"{item.get('contribution_rank')}. "
                f"**{item.get('component')}** — "
                f"{item.get('total_degradation')}"
            )

        lines.append("")
        lines.append("## Reproducibility")
        lines.append("")
        lines.append(
            "All reported evidence is derived from "
            "stored CRME evaluation artifacts. "
            "Raw evaluation outputs are preserved "
            "and are not modified by the aggregation layer."
        )

        with open(path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

    def _write_manifest(self, paths, path):
        manifest = {
            "manifest_version": "1.0",
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "purpose": (
                "Research provenance and "
                "reproducibility manifest "
                "for CRME evaluation evidence."
            ),
            "raw_sources": [
                {
                    "type": source_type,
                    "path": source_path,
                }
                for source_type, source_path
                in paths.items()
            ],
            "derived_outputs": [
                "evaluation_summary.json",
                "evaluation_summary.md",
                "tables/",
                "figures/",
            ],
            "raw_data_modified": False,
        }

        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                manifest,
                file,
                indent=4,
            )

    def aggregate(
        self,
        comparison_json,
        ablation_json,
        statistics_json,
    ):
        comparison = self._load_json(
            comparison_json
        )

        ablation = self._load_json(
            ablation_json
        )

        statistics = self._load_json(
            statistics_json
        )

        summary = {
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": "completed",
            "evaluation_pipeline": [
                "experiment",
                "comparison",
                "ablation",
                "statistics",
            ],
            "experiment": self._aggregate_experiment(
                comparison
            ),
            "comparison": self._aggregate_comparison(
                comparison
            ),
            "ablation": self._aggregate_ablation(
                ablation,
                statistics
            ),
            "statistics": self._aggregate_statistics(
                statistics
            ),
        }

        summary_path = os.path.join(
            self.output_dir,
            "evaluation_summary.json",
        )

        markdown_path = os.path.join(
            self.output_dir,
            "evaluation_summary.md",
        )

        manifest_path = os.path.join(
            self.output_dir,
            "evidence_manifest.json",
        )

        with open(
            summary_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                summary,
                file,
                indent=4,
            )

        self._write_markdown(
            summary,
            markdown_path,
        )

        self._write_manifest(
            {
                "comparison": comparison_json,
                "ablation": ablation_json,
                "statistics": statistics_json,
            },
            manifest_path,
        )

        return {
            "summary": summary_path,
            "markdown": markdown_path,
            "manifest": manifest_path,
            "output_dir": self.output_dir,
            "status": "completed",
        }
