import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path


class MultiRunEvaluationProtocol:
    """
    Registry and governance layer for independent CRME evaluation runs.

    Design principles:
    - Read-only with respect to canonical evidence
    - No synthetic replication of a single run
    - Duplicate-run detection
    - Explicit scenario/configuration tracking
    - Ready for paired statistical analysis
    """

    def __init__(self, base_path="."):
        self.base_path = Path(base_path)

        self.statistics_dir = (
            self.base_path / "evaluation/statistics"
        )

        self.results_dir = (
            self.base_path / "evaluation/results/final/statistics_v2"
        )

        self.registry_path = (
            self.statistics_dir / "run_registry.json"
        )

        self.statistics_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.results_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.registry = self._load_registry()

    # =========================================================
    # REGISTRY
    # =========================================================

    def _load_registry(self):
        if not self.registry_path.exists():
            return {
                "protocol": {
                    "name": "CRME Multi-Run Evaluation Protocol",
                    "version": "1.0.0",
                    "created_at": self._now(),
                },
                "runs": [],
            }

        try:
            with open(
                self.registry_path,
                "r",
                encoding="utf-8",
            ) as f:
                return json.load(f)
        except Exception:
            return {
                "protocol": {
                    "name": "CRME Multi-Run Evaluation Protocol",
                    "version": "1.0.0",
                    "created_at": self._now(),
                },
                "runs": [],
            }

    def _save_registry(self):
        with open(
            self.registry_path,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.registry,
                f,
                indent=4,
                ensure_ascii=False,
            )

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _now():
        return datetime.now(
            timezone.utc
        ).isoformat()

    @staticmethod
    def _fingerprint(
        dataset,
        scenario,
        configuration,
        metrics,
        metadata=None,
    ):
        payload = {
            "dataset": dataset,
            "scenario": scenario,
            "configuration": configuration,
            "metrics": metrics,
            "metadata": metadata or {},
        }

        serialized = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    # =========================================================
    # REGISTER RUN
    # =========================================================

    def register_run(
        self,
        run_id,
        dataset,
        scenario,
        configuration,
        metrics,
        source="runtime_evaluation",
        metadata=None,
    ):
        metadata = metadata or {}

        existing_ids = {
            run.get("run_id")
            for run in self.registry.get(
                "runs",
                [],
            )
        }

        if run_id in existing_ids:
            return {
                "status": "REJECTED",
                "reason": "duplicate_run_id",
                "run_id": run_id,
            }

        fingerprint = self._fingerprint(
            dataset=dataset,
            scenario=scenario,
            configuration=configuration,
            metrics=metrics,
            metadata=metadata,
        )

        existing_fingerprints = {
            run.get("fingerprint")
            for run in self.registry.get(
                "runs",
                [],
            )
        }

        if fingerprint in existing_fingerprints:
            return {
                "status": "REJECTED",
                "reason": "duplicate_run_content",
                "run_id": run_id,
                "fingerprint": fingerprint,
            }

        run = {
            "run_id": run_id,
            "created_at": self._now(),
            "dataset": dataset,
            "scenario": scenario,
            "configuration": configuration,
            "metrics": metrics,
            "source": source,
            "metadata": metadata,
            "fingerprint": fingerprint,
            "governance": {
                "canonical_evidence_mutated": False,
                "synthetic_replication": False,
                "independent_run_required": True,
            },
        }

        self.registry.setdefault(
            "runs",
            [],
        ).append(run)

        self._save_registry()

        return {
            "status": "REGISTERED",
            "run_id": run_id,
            "fingerprint": fingerprint,
            "total_runs": len(
                self.registry["runs"]
            ),
        }

    # =========================================================
    # QUERY
    # =========================================================

    def list_runs(
        self,
        scenario=None,
        configuration=None,
    ):
        runs = self.registry.get(
            "runs",
            [],
        )

        if scenario is not None:
            runs = [
                run
                for run in runs
                if run.get("scenario")
                == scenario
            ]

        if configuration is not None:
            runs = [
                run
                for run in runs
                if run.get("configuration")
                == configuration
            ]

        return runs

    # =========================================================
    # PAIRING
    # =========================================================

    def build_paired_groups(
        self,
        scenario=None,
    ):
        """
        Groups runs by scenario and metadata pairing key.

        A valid paired comparison requires:
        - same scenario
        - same dataset context
        - distinct configurations
        - explicit pairing_key
        """

        runs = self.list_runs(
            scenario=scenario,
        )

        groups = {}

        for run in runs:
            metadata = run.get(
                "metadata",
                {},
            )

            pairing_key = metadata.get(
                "pairing_key"
            )

            if not pairing_key:
                continue

            groups.setdefault(
                pairing_key,
                [],
            ).append(run)

        paired_groups = []

        for pairing_key, group in groups.items():

            configurations = {
                run.get(
                    "configuration"
                )
                for run in group
            }

            if len(configurations) >= 2:

                paired_groups.append(
                    {
                        "pairing_key": pairing_key,
                        "runs": group,
                        "configurations": sorted(
                            configurations
                        ),
                        "valid_for_paired_analysis": True,
                    }
                )

        return paired_groups

    # =========================================================
    # PROTOCOL STATUS
    # =========================================================

    def protocol_status(self):
        runs = self.registry.get(
            "runs",
            [],
        )

        unique_scenarios = {
            run.get(
                "scenario"
            )
            for run in runs
        }

        configurations = {
            run.get(
                "configuration"
            )
            for run in runs
        }

        return {
            "protocol": self.registry.get(
                "protocol",
                {},
            ),
            "total_runs": len(runs),
            "unique_scenarios": len(
                unique_scenarios
            ),
            "configurations": sorted(
                configurations
            ),
            "paired_groups": len(
                self.build_paired_groups()
            ),
            "statistical_readiness": (
                "READY_FOR_MULTI_RUN_ANALYSIS"
                if len(runs) >= 2
                else "SINGLE_RUN_ONLY"
            ),
        }

    # =========================================================
    # REPORT
    # =========================================================

    def export_report(self):

        report = {
            "created_at": self._now(),
            "protocol": self.registry.get(
                "protocol",
                {},
            ),
            "status": self.protocol_status(),
            "runs": self.registry.get(
                "runs",
                [],
            ),
            "paired_groups": self.build_paired_groups(),
        }

        json_path = (
            self.results_dir
            / "multi_run_protocol_report.json"
        )

        markdown_path = (
            self.results_dir
            / "multi_run_protocol_report.md"
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

        markdown = [
            "# CRME Multi-Run Evaluation Protocol",
            "",
            f"**Generated:** {report['created_at']}",
            "",
            "## Protocol Status",
            "",
            f"- Total runs: **{report['status']['total_runs']}**",
            f"- Unique scenarios: **{report['status']['unique_scenarios']}**",
            f"- Configurations: **{', '.join(report['status']['configurations']) or 'None'}**",
            f"- Paired groups: **{report['status']['paired_groups']}**",
            f"- Statistical readiness: **{report['status']['statistical_readiness']}**",
            "",
            "## Governance",
            "",
            "- Canonical evidence is not mutated.",
            "- Synthetic replication is prohibited.",
            "- Duplicate run content is rejected.",
            "- Independent evaluation runs are required for inferential analysis.",
            "",
            "## Registered Runs",
            "",
            "| Run ID | Scenario | Configuration | Dataset | Source |",
            "|---|---|---|---|---|",
        ]

        for run in report["runs"]:
            markdown.append(
                f"| {run.get('run_id')} | "
                f"{run.get('scenario')} | "
                f"{run.get('configuration')} | "
                f"{run.get('dataset')} | "
                f"{run.get('source')} |"
            )

        markdown.extend(
            [
                "",
                "## Paired Analysis Groups",
                "",
            ]
        )

        for group in report[
            "paired_groups"
        ]:
            markdown.append(
                f"- `{group['pairing_key']}`: "
                f"{', '.join(group['configurations'])}"
            )

        markdown_path.write_text(
            "\n".join(markdown),
            encoding="utf-8",
        )

        return {
            "json": str(json_path),
            "markdown": str(markdown_path),
            "status": "COMPLETED",
        }


if __name__ == "__main__":

    protocol = (
        MultiRunEvaluationProtocol()
    )

    print(
        protocol.export_report()
    )

