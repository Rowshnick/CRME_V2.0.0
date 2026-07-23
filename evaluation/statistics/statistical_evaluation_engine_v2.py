import json
import math
import random
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, pstdev, variance
from typing import Dict, List, Optional


# =========================================================
# CRME Statistical Evaluation Engine v2
# =========================================================
# Design principles:
# - Read-only access to canonical evidence
# - Backward compatible
# - No mutation of evaluation_summary.json
# - Supports repeated EvaluationRun objects
# - Ready for bootstrap, effect size, paired analysis,
#   multiple-comparison correction, and sensitivity analysis
# =========================================================


@dataclass
class EvaluationRun:
    run_id: str
    dataset: str
    scenario: str
    configuration: str
    metrics: Dict[str, float]
    source: str = "internal"
    metadata: Optional[Dict] = None

    def __post_init__(self):
        self.metrics = {
            str(k).upper(): float(v)
            for k, v in self.metrics.items()
        }

        if self.metadata is None:
            self.metadata = {}

    def to_dict(self):
        return asdict(self)


class StatisticalEvaluationEngineV2:

    def __init__(
        self,
        base_path=".",
        output_dir=None,
        random_seed=42,
    ):
        self.base_path = Path(base_path)

        self.summary_path = (
            self.base_path
            / "evaluation/results/final/evaluation_summary.json"
        )

        if output_dir is None:
            output_dir = (
                self.base_path
                / "evaluation/results/final/statistics_v2"
            )

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.random_seed = random_seed
        random.seed(random_seed)

        self.runs: List[EvaluationRun] = []

    # =====================================================
    # DATA INGESTION
    # =====================================================

    def add_run(self, run: EvaluationRun):
        if not isinstance(run, EvaluationRun):
            raise TypeError(
                "run must be an EvaluationRun instance"
            )

        self.runs.append(run)

    def add_runs(self, runs: List[EvaluationRun]):
        for run in runs:
            self.add_run(run)

    # =====================================================
    # CANONICAL EVIDENCE
    # =====================================================

    def load_canonical_baseline(self):
        """
        Read-only loader.

        This method never modifies evaluation_summary.json.
        """

        if not self.summary_path.exists():
            raise FileNotFoundError(
                f"Canonical summary not found: "
                f"{self.summary_path}"
            )

        with open(
            self.summary_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        metrics = (
            data
            .get("statistics", {})
            .get("baseline_metrics", {})
        )

        if not metrics:
            raise ValueError(
                "baseline_metrics not found in canonical "
                "evaluation summary"
            )

        return {
            str(k).upper(): float(v)
            for k, v in metrics.items()
        }

    def create_canonical_baseline_run(
        self,
        run_id="canonical-baseline-001",
        scenario="canonical_evaluation",
        configuration="crme",
    ):
        metrics = self.load_canonical_baseline()

        run = EvaluationRun(
            run_id=run_id,
            dataset="crme_internal",
            scenario=scenario,
            configuration=configuration,
            metrics=metrics,
            source="canonical_evaluation_summary",
        )

        self.add_run(run)

        return run

    # =====================================================
    # BASIC VALIDATION
    # =====================================================

    def _metric_names(self):
        names = set()

        for run in self.runs:
            names.update(run.metrics.keys())

        return sorted(names)

    def _values_for_metric(self, metric):
        metric = metric.upper()

        return [
            run.metrics[metric]
            for run in self.runs
            if metric in run.metrics
        ]

    # =====================================================
    # DESCRIPTIVE STATISTICS
    # =====================================================

    def descriptive_statistics(self):

        results = {}

        for metric in self._metric_names():

            values = self._values_for_metric(metric)

            if not values:
                continue

            n = len(values)

            result = {
                "metric": metric,
                "n": n,
                "mean": mean(values),
                "median": median(values),
                "min": min(values),
                "max": max(values),
            }

            if n > 1:
                result["population_std"] = pstdev(values)
                result["population_variance"] = variance(
                    values
                ) * (n - 1) / n
                result["sample_variance"] = variance(values)
                result["sample_std"] = math.sqrt(
                    variance(values)
                )
            else:
                result["population_std"] = 0.0
                result["population_variance"] = 0.0
                result["sample_variance"] = None
                result["sample_std"] = None

            sorted_values = sorted(values)

            if n >= 4:
                midpoint = n // 2

                if n % 2 == 0:
                    lower = sorted_values[:midpoint]
                    upper = sorted_values[midpoint:]
                else:
                    lower = sorted_values[:midpoint]
                    upper = sorted_values[midpoint + 1:]

                q1 = median(lower)
                q3 = median(upper)
                iqr = q3 - q1
            else:
                q1 = None
                q3 = None
                iqr = None

            result["q1"] = q1
            result["q3"] = q3
            result["iqr"] = iqr

            results[metric] = result

        return results

    # =====================================================
    # BOOTSTRAP CONFIDENCE INTERVAL
    # =====================================================

    def bootstrap_mean_ci(
        self,
        values,
        iterations=5000,
        confidence=0.95,
    ):

        values = list(values)

        if not values:
            return None

        if len(values) == 1:
            return {
                "mean": values[0],
                "lower": values[0],
                "upper": values[0],
                "iterations": iterations,
                "confidence": confidence,
                "note": (
                    "Single observation; inferential "
                    "uncertainty cannot be estimated."
                ),
            }

        bootstrap_means = []

        for _ in range(iterations):

            sample = random.choices(
                values,
                k=len(values),
            )

            bootstrap_means.append(
                mean(sample)
            )

        bootstrap_means.sort()

        alpha = 1 - confidence

        lower_index = int(
            (alpha / 2)
            * len(bootstrap_means)
        )

        upper_index = int(
            (1 - alpha / 2)
            * len(bootstrap_means)
        ) - 1

        return {
            "mean": mean(values),
            "lower": bootstrap_means[
                max(0, lower_index)
            ],
            "upper": bootstrap_means[
                min(
                    len(bootstrap_means) - 1,
                    upper_index,
                )
            ],
            "iterations": iterations,
            "confidence": confidence,
        }

    def bootstrap_confidence_intervals(
        self,
        iterations=5000,
        confidence=0.95,
    ):

        results = {}

        for metric in self._metric_names():

            values = self._values_for_metric(metric)

            results[metric] = (
                self.bootstrap_mean_ci(
                    values,
                    iterations=iterations,
                    confidence=confidence,
                )
            )

        return results

    # =====================================================
    # EFFECT SIZE
    # =====================================================

    def cohens_d(
        self,
        group_a,
        group_b,
    ):

        if not group_a or not group_b:
            return None

        mean_a = mean(group_a)
        mean_b = mean(group_b)

        if len(group_a) > 1:
            var_a = variance(group_a)
        else:
            var_a = 0.0

        if len(group_b) > 1:
            var_b = variance(group_b)
        else:
            var_b = 0.0

        n_a = len(group_a)
        n_b = len(group_b)

        denominator = (
            (n_a - 1) * var_a
            + (n_b - 1) * var_b
        )

        total_n = n_a + n_b - 2

        if total_n <= 0:
            return None

        pooled_variance = (
            denominator / total_n
        )

        pooled_std = math.sqrt(
            pooled_variance
        )

        if pooled_std == 0:
            return None

        return (
            mean_a - mean_b
        ) / pooled_std

    def effect_size(
        self,
        metric,
        configuration_a,
        configuration_b,
    ):

        metric = metric.upper()

        group_a = [
            run.metrics[metric]
            for run in self.runs
            if (
                run.configuration
                == configuration_a
                and metric in run.metrics
            )
        ]

        group_b = [
            run.metrics[metric]
            for run in self.runs
            if (
                run.configuration
                == configuration_b
                and metric in run.metrics
            )
        ]

        if not group_a or not group_b:
            return {
                "metric": metric,
                "status": "INSUFFICIENT_DATA",
            }

        mean_a = mean(group_a)
        mean_b = mean(group_b)

        absolute_difference = (
            mean_a - mean_b
        )

        if mean_b != 0:
            relative_change = (
                absolute_difference
                / abs(mean_b)
            ) * 100
        else:
            relative_change = None

        d = self.cohens_d(
            group_a,
            group_b,
        )

        return {
            "metric": metric,
            "configuration_a": configuration_a,
            "configuration_b": configuration_b,
            "n_a": len(group_a),
            "n_b": len(group_b),
            "mean_a": mean_a,
            "mean_b": mean_b,
            "absolute_difference": absolute_difference,
            "relative_change_percent": relative_change,
            "cohens_d": d,
        }

    # =====================================================
    # PAIRED DIFFERENCES
    # =====================================================

    def paired_differences(
        self,
        metric,
        configuration_a,
        configuration_b,
    ):

        metric = metric.upper()

        runs_a = {
            run.run_id: run
            for run in self.runs
            if (
                run.configuration
                == configuration_a
                and metric in run.metrics
            )
        }

        runs_b = {
            run.run_id: run
            for run in self.runs
            if (
                run.configuration
                == configuration_b
                and metric in run.metrics
            )
        }

        shared_ids = sorted(
            set(runs_a)
            & set(runs_b)
        )

        differences = []

        for run_id in shared_ids:

            differences.append(
                runs_a[run_id].metrics[metric]
                - runs_b[run_id].metrics[metric]
            )

        return {
            "metric": metric,
            "configuration_a": configuration_a,
            "configuration_b": configuration_b,
            "paired_run_count": len(differences),
            "differences": differences,
        }

    # =====================================================
    # SENSITIVITY ANALYSIS
    # =====================================================

    def sensitivity_analysis(
        self,
        metric,
        remove_each_observation=True,
    ):

        metric = metric.upper()

        values = self._values_for_metric(metric)

        if len(values) < 2:
            return {
                "metric": metric,
                "status": "INSUFFICIENT_DATA",
            }

        baseline_mean = mean(values)

        leave_one_out = []

        if remove_each_observation:

            for index in range(len(values)):

                reduced = (
                    values[:index]
                    + values[index + 1:]
                )

                leave_one_out.append(
                    {
                        "removed_index": index,
                        "removed_value": values[index],
                        "mean": mean(reduced),
                    }
                )

        means = [
            item["mean"]
            for item in leave_one_out
        ]

        return {
            "metric": metric,
            "baseline_mean": baseline_mean,
            "leave_one_out": leave_one_out,
            "min_leave_one_out_mean": min(means),
            "max_leave_one_out_mean": max(means),
            "range": max(means) - min(means),
        }

    # =====================================================
    # REPORT GENERATION
    # =====================================================

    def build_report(self):

        report = {
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "engine": {
                "name": (
                    "CRME Statistical Evaluation "
                    "Engine v2"
                ),
                "version": "2.0.0",
                "random_seed": self.random_seed,
            },

            "data_governance": {
                "canonical_evidence_mutated": False,
                "read_only_ingestion": True,
                "synthetic_inference_from_single_run": False,
            },

            "run_count": len(self.runs),

            "runs": [
                run.to_dict()
                for run in self.runs
            ],

            "descriptive_statistics": (
                self.descriptive_statistics()
            ),

            "bootstrap_confidence_intervals": (
                self.bootstrap_confidence_intervals()
            ),

            "status": (
                "DESCRIPTIVE_ANALYSIS_READY"
                if len(self.runs) >= 1
                else "NO_DATA"
            ),
        }

        return report

    def save_report(self):

        report = self.build_report()

        json_path = (
            self.output_dir
            / "statistical_evaluation_report.json"
        )

        md_path = (
            self.output_dir
            / "statistical_evaluation_report.md"
        )

        with open(
            json_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                report,
                f,
                indent=4,
                ensure_ascii=False,
            )

        markdown = self._to_markdown(report)

        with open(
            md_path,
            "w",
            encoding="utf-8",
        ) as f:

            f.write(markdown)

        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "run_count": len(self.runs),
            "status": report["status"],
        }

    # =====================================================
    # MARKDOWN
    # =====================================================

    def _to_markdown(self, report):

        lines = []

        lines.append(
            "# CRME Statistical Evaluation Engine v2"
        )

        lines.append("")

        lines.append(
            f"**Generated:** "
            f"{report['created_at']}"
        )

        lines.append("")

        lines.append(
            "## Governance"
        )

        lines.append("")

        lines.append(
            "- Canonical evidence mutated: **NO**"
        )

        lines.append(
            "- Read-only ingestion: **YES**"
        )

        lines.append(
            "- Synthetic inference from single run: **NO**"
        )

        lines.append("")

        lines.append(
            f"## Evaluation Runs: "
            f"{report['run_count']}"
        )

        lines.append("")

        if not report["runs"]:

            lines.append(
                "No evaluation runs available."
            )

        else:

            lines.append(
                "| Run ID | Dataset | Scenario | "
                "Configuration | Source |"
            )

            lines.append(
                "|---|---|---|---|---|"
            )

            for run in report["runs"]:

                lines.append(
                    "| "
                    f"{run['run_id']} | "
                    f"{run['dataset']} | "
                    f"{run['scenario']} | "
                    f"{run['configuration']} | "
                    f"{run['source']} |"
                )

        lines.append("")

        lines.append(
            "## Descriptive Statistics"
        )

        lines.append("")

        lines.append(
            "| Metric | n | Mean | Median | "
            "Min | Max | Std |"
        )

        lines.append(
            "|---|---:|---:|---:|---:|---:|---:|"
        )

        for metric, stats in (
            report[
                "descriptive_statistics"
            ].items()
        ):

            std = stats.get(
                "sample_std"
            )

            std_text = (
                "N/A"
                if std is None
                else f"{std:.4f}"
            )

            lines.append(
                "| "
                f"{metric} | "
                f"{stats['n']} | "
                f"{stats['mean']:.4f} | "
                f"{stats['median']:.4f} | "
                f"{stats['min']:.4f} | "
                f"{stats['max']:.4f} | "
                f"{std_text} |"
            )

        lines.append("")

        lines.append(
            "## Bootstrap Confidence Intervals"
        )

        lines.append("")

        lines.append(
            "Bootstrap intervals are descriptive "
            "when repeated observations are available. "
            "A single observation does not support "
            "valid inferential uncertainty estimation."
        )

        lines.append("")

        lines.append(
            "| Metric | Mean | Lower | Upper | "
            "Confidence |"
        )

        lines.append(
            "|---|---:|---:|---:|---:|"
        )

        for metric, ci in (
            report[
                "bootstrap_confidence_intervals"
            ].items()
        ):

            lines.append(
                "| "
                f"{metric} | "
                f"{ci['mean']:.4f} | "
                f"{ci['lower']:.4f} | "
                f"{ci['upper']:.4f} | "
                f"{ci['confidence']:.2f} |"
            )

        lines.append("")

        lines.append(
            "## Statistical Interpretation"
        )

        lines.append("")

        lines.append(
            "The current engine separates descriptive "
            "analysis from inferential claims. "
            "A single canonical evaluation run is "
            "treated as a point estimate and does not "
            "justify statistical significance claims."
        )

        lines.append("")

        lines.append(
            "**Status:** "
            f"`{report['status']}`"
        )

        return "\n".join(lines)


# =========================================================
# CLI / SMOKE TEST
# =========================================================

if __name__ == "__main__":

    engine = (
        StatisticalEvaluationEngineV2()
    )

    engine.create_canonical_baseline_run()

    result = engine.save_report()

    print(result)

