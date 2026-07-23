import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path


class MultiRunStatisticalAnalyzer:
    """
    CRME Multi-Run Statistical Analyzer

    Scientific policy:
    - Reads only observed evaluation runs.
    - Never synthesizes observations.
    - Does not infer statistical significance from a single run.
    - Uses descriptive analysis whenever inferential analysis is not justified.
    """

    VERSION = "1.0.0"

    def __init__(self, base_path="."):
        self.base_path = Path(base_path)

        self.statistics_dir = (
            self.base_path / "evaluation/statistics"
        )

        self.results_dir = (
            self.base_path
            / "evaluation/results/final/statistics_v2"
        )

        self.dataset_path = (
            self.results_dir
            / "multi_run_dataset.json"
        )

        self.output_dir = (
            self.results_dir
            / "multi_run_analysis"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.json_path = (
            self.output_dir
            / "multi_run_statistical_analysis_report.json"
        )

        self.markdown_path = (
            self.output_dir
            / "multi_run_statistical_analysis_report.md"
        )

    # =========================================================
    # HELPERS
    # =========================================================

    def _load_json(self, path):
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _safe_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _percentile(self, values, percentile):
        """
        Linear interpolation percentile.
        """
        if not values:
            return None

        values = sorted(values)

        if len(values) == 1:
            return values[0]

        position = (len(values) - 1) * percentile
        lower = math.floor(position)
        upper = math.ceil(position)

        if lower == upper:
            return values[int(position)]

        weight = position - lower

        return (
            values[lower]
            + weight * (values[upper] - values[lower])
        )

    # =========================================================
    # DATASET INGESTION
    # =========================================================

    def _extract_runs(self):
        dataset = self._load_json(self.dataset_path)

        if dataset is None:
            return {
                "status": "FAIL",
                "reason": "dataset_missing_or_invalid",
                "runs": [],
            }

        if isinstance(dataset, list):
            runs = dataset

        elif isinstance(dataset, dict):
            runs = dataset.get("runs", [])

        else:
            runs = []

        valid_runs = []

        for run in runs:
            if not isinstance(run, dict):
                continue

            metrics = run.get("metrics", {})

            if not isinstance(metrics, dict):
                continue

            normalized_metrics = {}

            for metric, value in metrics.items():
                numeric_value = self._safe_float(value)

                if numeric_value is not None:
                    normalized_metrics[
                        str(metric).upper()
                    ] = numeric_value

            if normalized_metrics:
                normalized_run = dict(run)
                normalized_run["metrics"] = normalized_metrics
                valid_runs.append(normalized_run)

        return {
            "status": "PASS",
            "reason": None,
            "runs": valid_runs,
        }

    # =========================================================
    # DESCRIPTIVE STATISTICS
    # =========================================================

    def _descriptive_statistics(self, values, metric):
        n = len(values)

        result = {
            "metric": metric,
            "n": n,
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            "population_std": None,
            "population_variance": None,
            "sample_std": None,
            "sample_variance": None,
            "q1": None,
            "q3": None,
            "iqr": None,
            "coefficient_of_variation": None,
        }

        if n == 0:
            return result

        result["mean"] = statistics.mean(values)
        result["median"] = statistics.median(values)
        result["min"] = min(values)
        result["max"] = max(values)

        if n >= 1:
            result["population_std"] = statistics.pstdev(values)
            result["population_variance"] = statistics.pvariance(values)

        if n >= 2:
            result["sample_std"] = statistics.stdev(values)
            result["sample_variance"] = statistics.variance(values)

        if n >= 2:
            result["q1"] = self._percentile(values, 0.25)
            result["q3"] = self._percentile(values, 0.75)
            result["iqr"] = (
                result["q3"] - result["q1"]
            )

        if result["mean"] not in (None, 0):
            std = result["sample_std"]

            if std is not None:
                result["coefficient_of_variation"] = (
                    std / result["mean"]
                )

        return result

    # =========================================================
    # BOOTSTRAP CI
    # =========================================================

    def _bootstrap_confidence_interval(
        self,
        values,
        iterations=5000,
        confidence=0.95,
    ):
        n = len(values)

        if n < 2:
            return {
                "mean": (
                    statistics.mean(values)
                    if values
                    else None
                ),
                "lower": None,
                "upper": None,
                "iterations": 0,
                "confidence": confidence,
                "status": "NOT_ESTIMABLE",
                "reason": (
                    "At least two independent observations "
                    "are required."
                ),
            }

        # Deterministic bootstrap without external dependencies.
        # Uses a reproducible pseudo-random generator.
        import random

        rng = random.Random(42)

        bootstrap_means = []

        for _ in range(iterations):
            sample = [
                values[rng.randrange(n)]
                for _ in range(n)
            ]

            bootstrap_means.append(
                statistics.mean(sample)
            )

        alpha = 1 - confidence

        lower = self._percentile(
            bootstrap_means,
            alpha / 2,
        )

        upper = self._percentile(
            bootstrap_means,
            1 - alpha / 2,
        )

        return {
            "mean": statistics.mean(values),
            "lower": lower,
            "upper": upper,
            "iterations": iterations,
            "confidence": confidence,
            "status": "ESTIMABLE",
        }

    # =========================================================
    # CORRELATION
    # =========================================================

    def _correlation_matrix(self, metric_values):
        metrics = sorted(metric_values.keys())

        matrix = {}

        for metric_a in metrics:
            matrix[metric_a] = {}

            for metric_b in metrics:
                values_a = metric_values[metric_a]
                values_b = metric_values[metric_b]

                paired = [
                    (a, b)
                    for a, b in zip(
                        values_a,
                        values_b,
                    )
                    if a is not None
                    and b is not None
                ]

                if len(paired) < 2:
                    matrix[metric_a][metric_b] = None
                    continue

                a_values = [x[0] for x in paired]
                b_values = [x[1] for x in paired]

                try:
                    matrix[metric_a][metric_b] = (
                        statistics.correlation(
                            a_values,
                            b_values,
                        )
                    )
                except Exception:
                    matrix[metric_a][metric_b] = None

        return matrix

    # =========================================================
    # ANALYSIS READINESS
    # =========================================================

    def _determine_readiness(self, run_count):
        if run_count <= 1:
            return {
                "status": "SINGLE_RUN_ONLY",
                "inferential_analysis": False,
                "descriptive_analysis": True,
            }

        if run_count < 5:
            return {
                "status": "MULTI_RUN_DESCRIPTIVE_READY",
                "inferential_analysis": False,
                "descriptive_analysis": True,
            }

        if run_count < 10:
            return {
                "status": "BOOTSTRAP_ANALYSIS_READY",
                "inferential_analysis": "LIMITED",
                "descriptive_analysis": True,
            }

        return {
            "status": "INFERENTIAL_ANALYSIS_READY",
            "inferential_analysis": True,
            "descriptive_analysis": True,
        }

    # =========================================================
    # MARKDOWN REPORT
    # =========================================================

    def _build_markdown(self, report):
        lines = []

        lines.append(
            "# CRME Multi-Run Statistical Analysis"
        )

        lines.append("")

        lines.append(
            f"**Generated:** "
            f"{report['created_at']}"
        )

        lines.append("")

        lines.append(
            f"**Statistical readiness:** "
            f"`{report['statistical_readiness']['status']}`"
        )

        lines.append("")

        lines.append("## Governance")

        lines.append("")

        lines.append(
            "- Observed runs only: **YES**"
        )

        lines.append(
            "- Synthetic observations generated: **NO**"
        )

        lines.append(
            "- Canonical evidence mutated: **NO**"
        )

        lines.append("")

        lines.append("## Run Summary")

        lines.append("")

        lines.append(
            f"- Total valid runs: "
            f"**{report['run_count']}**"
        )

        lines.append(
            f"- Unique scenarios: "
            f"**{report['unique_scenarios']}**"
        )

        lines.append(
            f"- Configurations: "
            f"**{', '.join(report['configurations']) or 'N/A'}**"
        )

        lines.append("")

        lines.append(
            "## Descriptive Statistics"
        )

        lines.append("")

        lines.append(
            "| Metric | n | Mean | Median | "
            "SD | Variance | CV |"
        )

        lines.append(
            "|---|---:|---:|---:|---:|---:|---:|"
        )

        for metric, stats in report[
            "descriptive_statistics"
        ].items():

            def fmt(value):
                if value is None:
                    return "N/A"

                return f"{value:.4f}"

            lines.append(
                f"| {metric} "
                f"| {stats['n']} "
                f"| {fmt(stats['mean'])} "
                f"| {fmt(stats['median'])} "
                f"| {fmt(stats['sample_std'])} "
                f"| {fmt(stats['sample_variance'])} "
                f"| {fmt(stats['coefficient_of_variation'])} |"
            )

        lines.append("")

        lines.append(
            "## Bootstrap Confidence Intervals"
        )

        lines.append("")

        lines.append(
            "| Metric | Mean | Lower | Upper | Status |"
        )

        lines.append(
            "|---|---:|---:|---:|---|"
        )

        for metric, ci in report[
            "bootstrap_confidence_intervals"
        ].items():

            def fmt(value):
                if value is None:
                    return "N/A"

                return f"{value:.4f}"

            lines.append(
                f"| {metric} "
                f"| {fmt(ci['mean'])} "
                f"| {fmt(ci['lower'])} "
                f"| {fmt(ci['upper'])} "
                f"| {ci['status']} |"
            )

        lines.append("")

        lines.append(
            "## Statistical Interpretation"
        )

        lines.append("")

        status = report[
            "statistical_readiness"
        ]["status"]

        if status == "SINGLE_RUN_ONLY":
            lines.append(
                "Only one observed evaluation run is "
                "available. Results are point estimates "
                "and no inferential statistical claims "
                "are justified."
            )

        elif status == "MULTI_RUN_DESCRIPTIVE_READY":
            lines.append(
                "Multiple observed runs are available. "
                "Descriptive variability analysis is "
                "supported, but inferential claims "
                "remain limited by sample size."
            )

        elif status == "BOOTSTRAP_ANALYSIS_READY":
            lines.append(
                "The number of observed runs supports "
                "descriptive analysis and exploratory "
                "bootstrap estimation. Inferential "
                "claims should remain conservative."
            )

        else:
            lines.append(
                "The observed run count supports "
                "advanced statistical analysis, subject "
                "to study design, independence, and "
                "assumption checks."
            )

        lines.append("")

        lines.append(
            "No statistical significance claim is "
            "generated automatically without adequate "
            "independent observations and an appropriate "
            "comparison design."
        )

        return "\n".join(lines)

    # =========================================================
    # MAIN ANALYSIS
    # =========================================================

    def analyze(self):
        ingestion = self._extract_runs()

        if ingestion["status"] != "PASS":
            report = {
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat(),

                "engine": {
                    "name": (
                        "CRME Multi-Run "
                        "Statistical Analyzer"
                    ),
                    "version": self.VERSION,
                },

                "status": "FAIL",
                "reason": ingestion["reason"],
            }

            self._write_report(report)

            return report

        runs = ingestion["runs"]

        metric_values = {}

        for run in runs:
            for metric, value in run[
                "metrics"
            ].items():

                metric_values.setdefault(
                    metric,
                    [],
                ).append(value)

        descriptive = {}

        for metric, values in metric_values.items():
            descriptive[metric] = (
                self._descriptive_statistics(
                    values,
                    metric,
                )
            )

        bootstrap = {}

        for metric, values in metric_values.items():
            bootstrap[metric] = (
                self._bootstrap_confidence_interval(
                    values
                )
            )

        scenarios = sorted(
            {
                run.get(
                    "scenario"
                )
                for run in runs
                if run.get("scenario")
            }
        )

        configurations = sorted(
            {
                run.get(
                    "configuration"
                )
                for run in runs
                if run.get("configuration")
            }
        )

        readiness = (
            self._determine_readiness(
                len(runs)
            )
        )

        report = {
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "engine": {
                "name": (
                    "CRME Multi-Run "
                    "Statistical Analyzer"
                ),
                "version": self.VERSION,
            },

            "data_governance": {
                "observed_runs_only": True,
                "synthetic_observations_generated": False,
                "canonical_evidence_mutated": False,
            },

            "run_count": len(runs),

            "unique_scenarios": len(
                scenarios
            ),

            "configurations": configurations,

            "statistical_readiness": readiness,

            "descriptive_statistics": descriptive,

            "bootstrap_confidence_intervals": bootstrap,

            "correlation_matrix": (
                self._correlation_matrix(
                    metric_values
                )
            ),

            "runs": runs,

            "status": "COMPLETED",
        }

        self._write_report(report)

        return report

    # =========================================================
    # OUTPUT
    # =========================================================

    def _write_report(self, report):
        with open(
            self.json_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                report,
                f,
                indent=4,
                ensure_ascii=False,
            )

        markdown = self._build_markdown(
            report
        )

        with open(
            self.markdown_path,
            "w",
            encoding="utf-8",
        ) as f:

            f.write(markdown)


if __name__ == "__main__":
    analyzer = MultiRunStatisticalAnalyzer()

    report = analyzer.analyze()

    print(
        {
            "json": str(
                analyzer.json_path
            ),
            "markdown": str(
                analyzer.markdown_path
            ),
            "run_count": report.get(
                "run_count",
                0,
            ),
            "statistical_readiness": report.get(
                "statistical_readiness",
                {},
            ),
            "status": report.get(
                "status"
            ),
        }
    )

