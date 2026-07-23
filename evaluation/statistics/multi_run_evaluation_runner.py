import json
import hashlib
import sys
import importlib
from datetime import datetime, timezone
from pathlib import Path

=========================================================

PROJECT ROOT PATH

=========================================================

PROJECT_ROOT = Path(file).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
sys.path.insert(0, str(PROJECT_ROOT))

class MultiRunEvaluationRunnerV2:
"""
CRME Multi-Run Evaluation Runner v2

Responsibilities:
- Execute independent evaluation runs through a real evaluator adapter.
- Store reproducible run metadata.
- Preserve canonical evidence.
- Prevent duplicate runs.
- Avoid synthetic metric generation.
- Prepare datasets for statistical analysis.
- Connect the real multi-run dataset to the
  MultiRunStatisticalAnalyzer.
- Preserve runner and analyzer outputs independently.
- Maintain strict evidence governance.
- Support direct execution from the CRME project root.
- Provide robust analyzer import resolution.
- Keep analyzer failures explicit and auditable.

The evaluator adapter must be a real callable:

    evaluator(
        scenario=scenario,
        configuration=configuration,
        seed=seed,
        run_id=run_id,
    )

and must return:

    {
        "MCS": 47.5,
        "SRS": 100.0,
        "KGQ": 40.0,
        "RRS": 43.33,
        "CES": 57.71,
    }
"""

VERSION = "2.0.0"

REQUIRED_METRICS = {
    "MCS",
    "SRS",
    "KGQ",
    "RRS",
    "CES",
}

def __init__(self, base_path="."):

    self.base_path = Path(base_path).resolve()

    self.summary_path = (
        self.base_path
        / "evaluation/results/final/evaluation_summary.json"
    )

    self.output_dir = (
        self.base_path
        / "evaluation/results/final/statistics_v2"
    )

    self.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    self.dataset_path = (
        self.output_dir
        / "multi_run_dataset.json"
    )

    self.report_path = (
        self.output_dir
        / "multi_run_runner_report.json"
    )

    self.markdown_path = (
        self.output_dir
        / "multi_run_runner_report.md"
    )

    # =====================================================
    # STATISTICAL ANALYZER OUTPUTS
    # =====================================================

    self.statistical_analysis_report_path = (
        self.output_dir
        / "multi_run_statistical_analysis_report.json"
    )

    self.statistical_analysis_markdown_path = (
        self.output_dir
        / "multi_run_statistical_analysis_report.md"
    )

# =========================================================
# JSON HELPERS
# =========================================================

def _load_json(self, path):

    path = Path(path)

    if not path.exists():

        return None

    try:

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    except Exception:

        return None

def _save_json(
    self,
    path,
    data,
):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False,
        )

# =========================================================
# DATASET
# =========================================================

def _load_dataset(self):

    dataset = self._load_json(
        self.dataset_path
    )

    if not dataset:

        return {

            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "dataset_name": (
                "crme_multi_run_evaluation"
            ),

            "runner_version": self.VERSION,

            "governance": {

                "canonical_evidence_mutated": False,

                "read_only_ingestion": True,

                "synthetic_metrics_generated": False,
            },

            "runs": [],
        }

    return dataset

def _save_dataset(
    self,
    dataset,
):

    self._save_json(
        self.dataset_path,
        dataset,
    )

# =========================================================
# RUN ID
# =========================================================

def build_run_id(
    self,
    scenario,
    configuration,
    seed,
):
    """
    Deterministic run ID.

    Same scenario + configuration + seed
    always produces the same run ID.
    """

    raw = (
        f"{scenario}|"
        f"{configuration}|"
        f"{seed}"
    )

    digest = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:10]

    return (
        f"run-{scenario}-"
        f"{configuration}-"
        f"seed-{seed}-"
        f"{digest}"
    )

# =========================================================
# METRIC VALIDATION
# =========================================================

def _validate_metrics(
    self,
    metrics,
):

    if not isinstance(
        metrics,
        dict,
    ):

        raise TypeError(
            "Evaluator must return a dictionary."
        )

    normalized = {}

    for key, value in metrics.items():

        try:

            normalized[
                str(key).upper()
            ] = float(value)

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                f"Metric {key} must be numeric."
            )

    missing = (
        self.REQUIRED_METRICS
        - set(normalized.keys())
    )

    if missing:

        raise ValueError(
            "Missing required metrics: "
            f"{sorted(missing)}"
        )

    invalid = []

    for metric in self.REQUIRED_METRICS:

        value = normalized[metric]

        if value < 0:

            invalid.append(
                f"{metric}: negative value"
            )

    if invalid:

        raise ValueError(
            "Invalid metrics: "
            f"{invalid}"
        )

    return {

        metric: normalized[metric]

        for metric in sorted(
            self.REQUIRED_METRICS
        )
    }

# =========================================================
# RUN CREATION
# =========================================================

def _build_run(
    self,
    run_id,
    scenario,
    configuration,
    seed,
    metrics,
    evaluator_name,
    metadata=None,
):

    return {

        "run_id": run_id,

        "dataset": "crme_internal",

        "scenario": scenario,

        "configuration": configuration,

        "seed": seed,

        "metrics": metrics,

        "evaluator": evaluator_name,

        "source": (
            "real_evaluation_pipeline"
        ),

        "metadata": metadata or {},

        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

# =========================================================
# EXECUTE ONE RUN
# =========================================================

def execute_run(
    self,
    evaluator,
    scenario,
    configuration,
    seed,
    evaluator_name="unknown",
    metadata=None,
):
    """
    Execute one real evaluation run.

    No synthetic metrics are generated here.
    """

    if not callable(
        evaluator
    ):

        raise TypeError(
            "evaluator must be callable."
        )

    run_id = self.build_run_id(

        scenario=scenario,

        configuration=configuration,

        seed=seed,
    )

    dataset = self._load_dataset()

    existing_ids = {

        run.get(
            "run_id"
        )

        for run in dataset.get(
            "runs",
            [],
        )
    }

    if run_id in existing_ids:

        return {

            "status": (
                "SKIPPED_DUPLICATE"
            ),

            "run_id": run_id,
        }

    metrics = evaluator(

        scenario=scenario,

        configuration=configuration,

        seed=seed,

        run_id=run_id,
    )

    metrics = self._validate_metrics(
        metrics
    )

    run = self._build_run(

        run_id=run_id,

        scenario=scenario,

        configuration=configuration,

        seed=seed,

        metrics=metrics,

        evaluator_name=evaluator_name,

        metadata=metadata,
    )

    dataset.setdefault(
        "runs",
        []
    ).append(
        run
    )

    self._save_dataset(
        dataset
    )

    return {

        "status": "COMPLETED",

        "run": run,
    }

# =========================================================
# BATCH EXECUTION
# =========================================================

def execute_batch(
    self,
    evaluator,
    scenarios,
    configurations,
    seeds,
    evaluator_name="unknown",
    metadata=None,
):
    """
    Execute a real factorial evaluation design.

    Every combination of:

        scenario
        configuration
        seed

    is evaluated independently.
    """

    results = []

    for scenario in scenarios:

        for configuration in configurations:

            for seed in seeds:

                result = self.execute_run(

                    evaluator=evaluator,

                    scenario=scenario,

                    configuration=configuration,

                    seed=seed,

                    evaluator_name=evaluator_name,

                    metadata=metadata,
                )

                results.append(
                    result
                )

    return results

# =========================================================
# DATASET VALIDATION
# =========================================================

def validate_dataset(self):

    dataset = self._load_dataset()

    runs = dataset.get(
        "runs",
        [],
    )

    run_ids = [

        run.get(
            "run_id"
        )

        for run in runs
    ]

    duplicate_ids = (

        len(run_ids)

        != len(
            set(run_ids)
        )
    )

    invalid_runs = []

    for run in runs:

        if not run.get(
            "run_id"
        ):

            invalid_runs.append(
                "missing_run_id"
            )

        if not run.get(
            "scenario"
        ):

            invalid_runs.append(
                "missing_scenario"
            )

        if not run.get(
            "configuration"
        ):

            invalid_runs.append(
                "missing_configuration"
            )

        try:

            self._validate_metrics(

                run.get(
                    "metrics",
                    {},
                )
            )

        except Exception as exc:

            invalid_runs.append(
                str(exc)
            )

    return {

        "total_runs": len(
            runs
        ),

        "duplicate_run_ids": (
            duplicate_ids
        ),

        "invalid_runs": (
            invalid_runs
        ),

        "valid": (

            not duplicate_ids

            and not invalid_runs
        ),
    }

# =========================================================
# STATISTICAL READINESS
# =========================================================

def _statistical_readiness(
    self,
    runs,
):

    total_runs = len(
        runs
    )

    if total_runs < 2:

        return (
            "SINGLE_RUN_ONLY"
        )

    scenario_count = len(

        {

            run.get(
                "scenario"
            )

            for run in runs
        }
    )

    configuration_count = len(

        {

            run.get(
                "configuration"
            )

            for run in runs
        }
    )

    if (

        scenario_count >= 2

        and configuration_count >= 2
    ):

        return (

            "MULTI_SCENARIO_COMPARISON_READY"
        )

    if total_runs >= 10:

        return (

            "DESCRIPTIVE_ANALYSIS_READY"
        )

    return (

        "MULTI_RUN_DESCRIPTIVE_READY"
    )

# =========================================================
# ANALYZER IMPORT RESOLUTION
# =========================================================

def _resolve_statistical_analyzer_class(self):

    """
    Resolve MultiRunStatisticalAnalyzer robustly.

    Primary path:

        evaluation.statistics.multi_run_statistical_analyzer

    Fallback path:

        Direct module loading from the project filesystem.

    This prevents the runner from failing merely because
    the package is executed directly from Termux.
    """

    import_error = None

    # -----------------------------------------------------
    # PRIMARY IMPORT
    # -----------------------------------------------------

    try:

        module = importlib.import_module(

            "evaluation.statistics.multi_run_statistical_analyzer"
        )

        analyzer_class = getattr(

            module,

            "MultiRunStatisticalAnalyzer"
        )

        return {

            "status": "RESOLVED",

            "class": analyzer_class,

            "import_path": (

                "evaluation.statistics."
                "multi_run_statistical_analyzer"
            ),

            "error": None,
        }

    except Exception as exc:

        import_error = exc

    # -----------------------------------------------------
    # FALLBACK FILE RESOLUTION
    # -----------------------------------------------------

    analyzer_path = (

        self.base_path

        / "evaluation/statistics/"
          "multi_run_statistical_analyzer.py"
    )

    if not analyzer_path.exists():

        return {

            "status": "FAILED",

            "class": None,

            "import_path": None,

            "error": (

                "Analyzer module not found. "

                f"Expected path: {analyzer_path}. "

                f"Primary import error: {import_error}"
            ),
        }

    try:

        import importlib.util

        module_name = (
            "crme_multi_run_statistical_analyzer"
        )

        spec = (

            importlib.util.spec_from_file_location(

                module_name,

                analyzer_path,
            )
        )

        if spec is None:

            raise ImportError(

                "Could not create module specification."
            )

        module = (

            importlib.util.module_from_spec(
                spec
            )
        )

        sys.modules[
            module_name
        ] = module

        spec.loader.exec_module(
            module
        )

        analyzer_class = getattr(

            module,

            "MultiRunStatisticalAnalyzer"
        )

        return {

            "status": "RESOLVED_FALLBACK",

            "class": analyzer_class,

            "import_path": str(
                analyzer_path
            ),

            "error": None,
        }

    except Exception as exc:

        return {

            "status": "FAILED",

            "class": None,

            "import_path": str(
                analyzer_path
            ),

            "error": (

                "Fallback analyzer loading failed. "

                f"Primary import error: {import_error}. "

                f"Fallback error: {exc}"
            ),
        }

# =========================================================
# MULTI-RUN STATISTICAL ANALYSIS
# =========================================================

def run_statistical_analysis(self):

    """
    Run the real MultiRunStatisticalAnalyzer
    against the dataset generated by this runner.

    The analyzer must consume the existing dataset.

    No synthetic runs are created here.
    """

    resolution = (

        self._resolve_statistical_analyzer_class()
    )

    if resolution[
        "status"
    ] not in {

        "RESOLVED",

        "RESOLVED_FALLBACK",
    }:

        return {

            "status": (
                "ANALYZER_IMPORT_ERROR"
            ),

            "error": resolution[
                "error"
            ],

            "json": None,

            "markdown": None,

            "import_path": resolution[
                "import_path"
            ],
        }

    analyzer_class = (

        resolution[
            "class"
        ]
    )

    try:

        analyzer = analyzer_class(

            base_path=self.base_path
        )

        analysis_report = (

            analyzer.analyze()
        )

        if isinstance(

            analysis_report,

            dict,
        ):

            analysis_json = (

                analysis_report.get(
                    "json"
                )

                or analysis_report.get(
                    "report_path"
                )

                or analysis_report.get(
                    "analysis_json"
                )
            )

            analysis_markdown = (

                analysis_report.get(
                    "markdown"
                )

                or analysis_report.get(
                    "markdown_path"
                )

                or analysis_report.get(
                    "analysis_markdown"
                )
            )

            return {

                "status": (

                    analysis_report.get(

                        "status",

                        "COMPLETED",
                    )
                ),

                "json": analysis_json,

                "markdown": analysis_markdown,

                "report": analysis_report,

                "import_path": resolution[
                    "import_path"
                ],
            }

        return {

            "status": "COMPLETED",

            "json": None,

            "markdown": None,

            "report": analysis_report,

            "import_path": resolution[
                "import_path"
            ],
        }

    except Exception as exc:

        return {

            "status": (
                "ANALYZER_ERROR"
            ),

            "error": str(
                exc
            ),

            "json": None,

            "markdown": None,

            "import_path": resolution[
                "import_path"
            ],
        }

# =========================================================
# SUMMARY
# =========================================================

def build_report(
    self,
    run_statistical_analysis=True,
):

    dataset = self._load_dataset()

    runs = dataset.get(
        "runs",
        [],
    )

    validation = (

        self.validate_dataset()
    )

    scenarios = sorted(

        {

            run.get(
                "scenario"
            )

            for run in runs
        }
    )

    configurations = sorted(

        {

            run.get(
                "configuration"
            )

            for run in runs
        }
    )

    seeds = sorted(

        {

            run.get(
                "seed"
            )

            for run in runs

            if run.get(
                "seed"
            )
            is not None
        }
    )

    statistical_analysis = None

    if run_statistical_analysis:

        statistical_analysis = (

            self.run_statistical_analysis()
        )

    report = {

        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "runner": {

            "name": (

                "CRME Multi-Run "
                "Evaluation Runner"
            ),

            "version": self.VERSION,
        },

        "governance": {

            "canonical_evidence_mutated": False,

            "read_only_ingestion": True,

            "synthetic_metrics_generated": False,
        },

        "dataset": {

            "path": str(
                self.dataset_path
            ),

            "total_runs": len(
                runs
            ),

            "unique_scenarios": len(
                scenarios
            ),

            "unique_configurations": len(
                configurations
            ),

            "unique_seeds": len(
                seeds
            ),

            "scenarios": scenarios,

            "configurations": configurations,

            "seeds": seeds,
        },

        "validation": validation,

        "statistical_readiness": (

            self._statistical_readiness(
                runs
            )
        ),

        "statistical_analysis": (

            statistical_analysis
        ),

        "runs": runs,

        "status": (

            "READY"

            if validation[
                "valid"
            ]

            else "INVALID_DATASET"
        ),
    }

    self._save_json(

        self.report_path,

        report,
    )

    self._write_markdown(

        report
    )

    return report

# =========================================================
# MARKDOWN
# =========================================================

def _write_markdown(
    self,
    report,
):

    lines = []

    lines.append(

        "# CRME Multi-Run Evaluation Runner v2"
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

    governance = (

        report[
            "governance"
        ]
    )

    lines.append(

        "- Canonical evidence mutated: "

        f"**{governance['canonical_evidence_mutated']}**"
    )

    lines.append(

        "- Read-only ingestion: "

        f"**{governance['read_only_ingestion']}**"
    )

    lines.append(

        "- Synthetic metrics generated: "

        f"**{governance['synthetic_metrics_generated']}**"
    )

    lines.append("")

    lines.append(

        "## Dataset Summary"
    )

    lines.append("")

    dataset = (

        report[
            "dataset"
        ]
    )

    lines.append(

        f"- Total runs: "

        f"**{dataset['total_runs']}**"
    )

    lines.append(

        f"- Unique scenarios: "

        f"**{dataset['unique_scenarios']}**"
    )

    lines.append(

        f"- Unique configurations: "

        f"**{dataset['unique_configurations']}**"
    )

    lines.append(

        f"- Unique seeds: "

        f"**{dataset['unique_seeds']}**"
    )

    lines.append("")

    lines.append(

        "## Statistical Readiness"
    )

    lines.append("")

    lines.append(

        f"**{report['statistical_readiness']}**"
    )

    lines.append("")

    lines.append(

        "## Statistical Analyzer"
    )

    lines.append("")

    statistical_analysis = (

        report.get(
            "statistical_analysis"
        )
    )

    if statistical_analysis:

        lines.append(

            f"- Status: "

            f"**{statistical_analysis.get('status')}**"
        )

        if statistical_analysis.get(
            "import_path"
        ):

            lines.append(

                "- Import path: "

                f"`{statistical_analysis['import_path']}`"
            )

        if statistical_analysis.get(
            "json"
        ):

            lines.append(

                "- JSON report: "

                f"`{statistical_analysis['json']}`"
            )

        if statistical_analysis.get(
            "markdown"
        ):

            lines.append(

                "- Markdown report: "

                f"`{statistical_analysis['markdown']}`"
            )

        if statistical_analysis.get(
            "error"
        ):

            lines.append(

                "- Error: "

                f"`{statistical_analysis['error']}`"
            )

    else:

        lines.append(

            "Statistical analysis was not executed."
        )

    lines.append("")

    lines.append(

        "## Validation"
    )

    lines.append("")

    validation = (

        report[
            "validation"
        ]
    )

    lines.append(

        f"- Dataset valid: "

        f"**{validation['valid']}**"
    )

    lines.append(

        f"- Total runs: "

        f"**{validation['total_runs']}**"
    )

    lines.append(

        f"- Duplicate run IDs: "

        f"**{validation['duplicate_run_ids']}**"
    )

    lines.append("")

    lines.append(

        "## Runs"
    )

    lines.append("")

    lines.append(

        "| Run ID | Scenario | "
        "Configuration | Seed |"
    )

    lines.append(

        "|---|---|---|---:|"
    )

    for run in report[
        "runs"
    ]:

        lines.append(

            "| "

            f"{run.get('run_id')} | "

            f"{run.get('scenario')} | "

            f"{run.get('configuration')} | "

            f"{run.get('seed')} |"
        )

    lines.append("")

    self.markdown_path.write_text(

        "\n".join(
            lines
        ),

        encoding="utf-8",
    )

# =========================================================
# MAIN
# =========================================================

def run(
    self,
    evaluator=None,
    scenarios=None,
    configurations=None,
    seeds=None,
    evaluator_name="unknown",
    metadata=None,
    run_statistical_analysis=True,
):
    """
    Run the orchestrator.

    If evaluator is None:

        Only validates existing dataset and
        runs statistical analysis.

    If evaluator is supplied:

        Executes the real factorial experiment
        and then analyzes the resulting dataset.
    """

    if evaluator is not None:

        if not scenarios:

            raise ValueError(

                "scenarios are required."
            )

        if not configurations:

            raise ValueError(

                "configurations are required."
            )

        if not seeds:

            raise ValueError(

                "seeds are required."
            )

        self.execute_batch(

            evaluator=evaluator,

            scenarios=scenarios,

            configurations=configurations,

            seeds=seeds,

            evaluator_name=evaluator_name,

            metadata=metadata,
        )

    report = (

        self.build_report(

            run_statistical_analysis=(

                run_statistical_analysis
            )
        )
    )

    return {

        "json": str(

            self.report_path
        ),

        "markdown": str(

            self.markdown_path
        ),

        "dataset": str(

            self.dataset_path
        ),

        "run_count": report[

            "dataset"
        ][

            "total_runs"
        ],

        "statistical_readiness": (

            report[

                "statistical_readiness"
            ]
        ),

        "statistical_analysis": (

            report.get(

                "statistical_analysis"
            )
        ),

        "status": report[

            "status"
        ],
    }

if name == "main":

runner = (

    MultiRunEvaluationRunnerV2(

        base_path=PROJECT_ROOT
    )
)

print(

    runner.run()
)

