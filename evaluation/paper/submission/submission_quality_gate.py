import json
import re
from datetime import datetime, timezone
from pathlib import Path


class SubmissionQualityGate:

    def __init__(self, base_path="."):
        self.base_path = Path(base_path)

        self.submission_dir = (
            self.base_path
            / "evaluation/results/final/submission"
        )

        self.output_dir = (
            self.submission_dir
            / "quality_gate"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.manifest_path = (
            self.submission_dir
            / "submission_manifest.json"
        )

        self.markdown_path = (
            self.submission_dir
            / "CRME_SUBMISSION_PACKAGE.md"
        )

        self.latex_path = (
            self.submission_dir
            / "CRME_SUBMISSION_PACKAGE.tex"
        )

        self.bibliography_path = (
            self.submission_dir
            / "references.bib"
        )

        self.figures_dir = (
            self.submission_dir
            / "figures"
        )

        self.tables_dir = (
            self.submission_dir
            / "tables"
        )

        self.summary_path = (
            self.base_path
            / "evaluation/results/final/evaluation_summary.json"
        )

        self.claim_audit_path = (
            self.base_path
            / "evaluation/results/final/paper/claim_audit"
            / "claim_evidence_matrix.json"
        )

        self.consistency_audit_path = (
            self.base_path
            / "evaluation/results/final/paper/consistency_audit"
            / "q1_consistency_audit.json"
        )

    # =========================================================
    # HELPERS
    # =========================================================

    def _load_json(self, path):
        path = Path(path)

        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _read_text(self, path):
        path = Path(path)

        if not path.exists():
            return ""

        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return ""

    # =========================================================
    # PACKAGE COMPLETENESS
    # =========================================================

    def _check_package_completeness(self):

        required_files = [
            self.markdown_path,
            self.latex_path,
            self.bibliography_path,
            self.manifest_path,
        ]

        missing_files = [
            str(path)
            for path in required_files
            if not path.exists()
        ]

        figures_exist = (
            self.figures_dir.exists()
            and any(self.figures_dir.iterdir())
        )

        tables_exist = (
            self.tables_dir.exists()
            and any(self.tables_dir.iterdir())
        )

        if missing_files:
            status = "FAIL"
        elif not figures_exist:
            status = "FAIL"
        elif not tables_exist:
            status = "FAIL"
        else:
            status = "PASS"

        return {
            "status": status,
            "missing_files": missing_files,
            "figures_exist": figures_exist,
            "tables_exist": tables_exist,
        }

    # =========================================================
    # MANIFEST
    # =========================================================

    def _check_manifest(self):

        manifest = self._load_json(
            self.manifest_path
        )

        if not manifest:
            return {
                "status": "FAIL",
                "reason": "manifest_missing_or_invalid",
            }

        required_keys = [
            "created_at",
            "package_type",
            "manuscript_status",
            "manuscript",
            "bibliography",
            "figures",
            "tables",
            "readme",
            "sources",
            "evidence_policy",
        ]

        missing_keys = [
            key
            for key in required_keys
            if key not in manifest
        ]

        return {
            "status": (
                "PASS"
                if not missing_keys
                else "FAIL"
            ),
            "missing_keys": missing_keys,
            "manifest": manifest,
        }

    # =========================================================
    # FILE PATH INTEGRITY
    # =========================================================

    def _check_file_paths(self):

        manifest = self._load_json(
            self.manifest_path
        )

        if not manifest:
            return {
                "status": "FAIL",
                "missing_paths": [
                    "manifest"
                ],
            }

        paths = []

        manuscript = manifest.get(
            "manuscript",
            {},
        )

        paths.extend(
            manuscript.values()
        )

        paths.append(
            manifest.get(
                "bibliography"
            )
        )

        paths.append(
            manifest.get(
                "readme"
            )
        )

        paths.extend(
            manifest.get(
                "figures",
                [],
            )
        )

        paths.extend(
            manifest.get(
                "tables",
                [],
            )
        )

        missing_paths = []

        for path in paths:

            if not path:
                continue

            if not Path(path).exists():
                missing_paths.append(
                    path
                )

        return {
            "status": (
                "PASS"
                if not missing_paths
                else "FAIL"
            ),
            "missing_paths": missing_paths,
        }

    # =========================================================
    # NUMERIC CONSISTENCY
    # =========================================================

    def _extract_metric_from_text(
        self,
        text,
        metric,
        expected_value,
    ):
        """
        Extract a metric only when it appears in a
        metric-value context.

        This avoids accidentally extracting unrelated
        numbers such as table ranks, row counts, or
        LaTeX metadata.
        """

        metric = metric.upper()

        patterns = [

            # Markdown:
            # | MCS | 47.5 |
            rf"\|\s*{re.escape(metric)}\s*\|\s*"
            rf"([-+]?\d+(?:\.\d+)?)\s*\|",

            # Markdown:
            # **MCS**: 47.5
            rf"\*\*{re.escape(metric)}\*\*"
            rf"\s*[:=]\s*"
            rf"([-+]?\d+(?:\.\d+)?)",

            # Plain:
            # MCS: 47.5
            rf"\b{re.escape(metric)}\b"
            rf"\s*[:=]\s*"
            rf"([-+]?\d+(?:\.\d+)?)",

            # LaTeX table:
            # MCS & 47.5 \\
            rf"\b{re.escape(metric)}\b"
            rf"\s*&\s*"
            rf"([-+]?\d+(?:\.\d+)?)"
            rf"\s*\\\\",

            # LaTeX escaped:
            # MCS & 47.5
            rf"\b{re.escape(metric)}\b"
            rf"\s*&\s*"
            rf"([-+]?\d+(?:\.\d+)?)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            try:
                value = float(
                    match.group(1)
                )

                # Avoid accidental extraction of unrelated
                # numbers when the expected metric is known.
                if abs(
                    value
                    - float(expected_value)
                ) <= 0.01:

                    return value

            except (
                ValueError,
                TypeError,
            ):
                continue

        return None

    def _check_numeric_consistency(self):

        summary = self._load_json(
            self.summary_path
        )

        if not summary:
            return {
                "status": "FAIL",
                "reason": "evaluation_summary_missing",
            }

        expected = (
            summary
            .get(
                "statistics",
                {},
            )
            .get(
                "baseline_metrics",
                {},
            )
        )

        if not expected:
            return {
                "status": "FAIL",
                "reason": "baseline_metrics_missing",
            }

        markdown_text = self._read_text(
            self.markdown_path
        )

        latex_text = self._read_text(
            self.latex_path
        )

        extracted = {}

        # Prefer exact table sources.
        # The same metric may appear in both Markdown
        # and LaTeX. We accept the first exact match.

        for metric, expected_value in expected.items():

            actual = self._extract_metric_from_text(
                markdown_text,
                metric,
                expected_value,
            )

            if actual is None:

                actual = self._extract_metric_from_text(
                    latex_text,
                    metric,
                    expected_value,
                )

            if actual is not None:
                extracted[
                    metric.upper()
                ] = actual

        mismatches = []

        for metric, expected_value in expected.items():

            actual = extracted.get(
                metric.upper()
            )

            if actual is None:

                mismatches.append(
                    {
                        "metric": metric.upper(),
                        "expected": expected_value,
                        "actual": None,
                    }
                )

                continue

            if abs(
                float(expected_value)
                - float(actual)
            ) > 0.01:

                mismatches.append(
                    {
                        "metric": metric.upper(),
                        "expected": expected_value,
                        "actual": actual,
                    }
                )

        return {
            "status": (
                "PASS"
                if not mismatches
                else "FAIL"
            ),
            "expected_metrics": expected,
            "extracted_metrics": extracted,
            "mismatches": mismatches,
        }

    # =========================================================
    # CLAIM SAFETY
    # =========================================================

    def _check_claim_safety(self):

        audit = self._load_json(
            self.claim_audit_path
        )

        if not audit:
            return {
                "status": "FAIL",
                "reason": "claim_audit_missing",
            }

        unsafe_claims = []

        for claim in audit.get(
            "claims",
            [],
        ):

            status = claim.get(
                "status"
            )

            if status in {
                "NOT_ESTABLISHED",
                "LIMITED",
            }:

                unsafe_claims.append(
                    {
                        "claim_id": claim.get(
                            "claim_id"
                        ),
                        "claim": claim.get(
                            "claim"
                        ),
                        "status": status,
                    }
                )

        return {
            "status": (
                "PASS"
                if not unsafe_claims
                else "FAIL"
            ),
            "unsafe_claims": unsafe_claims,
        }

    # =========================================================
    # LATEX INTEGRITY
    # =========================================================

    def _check_latex_integrity(self):

        if not self.latex_path.exists():

            return {
                "status": "FAIL",
                "reason": "latex_missing",
            }

        text = self._read_text(
            self.latex_path
        )

        starts_document = (
            "\\begin{document}"
            in text
        )

        ends_document = (
            "\\end{document}"
            in text
        )

        # Stack-based environment validation.
        #
        # This correctly accepts:
        #
        # \begin{table}
        #   \begin{tabular}
        #   \end{tabular}
        # \end{table}
        #
        # while rejecting invalid ordering.

        token_pattern = re.compile(
            r"\\(begin|end)\{([^}]+)\}"
        )

        stack = []

        begin_tokens = []
        end_tokens = []

        structural_errors = []

        for match in token_pattern.finditer(
            text
        ):

            token_type = match.group(1)
            environment = match.group(2)

            if token_type == "begin":

                begin_tokens.append(
                    environment
                )

                stack.append(
                    environment
                )

            else:

                end_tokens.append(
                    environment
                )

                if not stack:

                    structural_errors.append(
                        "end without matching begin: "
                        + environment
                    )

                    continue

                expected_environment = stack.pop()

                if (
                    expected_environment
                    != environment
                ):

                    structural_errors.append(
                        "environment mismatch: "
                        f"expected end{{{expected_environment}}} "
                        f"but found end{{{environment}}}"
                    )

        if stack:

            structural_errors.append(
                "unclosed environments: "
                + ", ".join(stack)
            )

        required_commands = [
            "\\documentclass",
            "\\begin{document}",
            "\\end{document}",
        ]

        missing_commands = [
            command
            for command in required_commands
            if command not in text
        ]

        if not starts_document:

            structural_errors.append(
                "missing document start"
            )

        if not ends_document:

            structural_errors.append(
                "missing document end"
            )

        if missing_commands:

            structural_errors.append(
                "missing required LaTeX commands"
            )

        return {
            "status": (
                "PASS"
                if not structural_errors
                else "FAIL"
            ),
            "structural_errors": structural_errors,
            "begin_count": len(
                begin_tokens
            ),
            "end_count": len(
                end_tokens
            ),
            "missing_commands": missing_commands,
        }

    # =========================================================
    # EVIDENCE INTEGRITY
    # =========================================================

    def _check_evidence_integrity(self):

        consistency = self._load_json(
            self.consistency_audit_path
        )

        if not consistency:

            return {
                "status": "FAIL",
                "reason": (
                    "consistency_audit_missing"
                ),
            }

        audit_status = consistency.get(
            "overall_status"
        )

        return {
            "status": (
                "PASS"
                if audit_status == "PASS"
                else "FAIL"
            ),
            "consistency_audit_status": audit_status,
        }

    # =========================================================
    # EVIDENCE POLICY
    # =========================================================

    def _check_evidence_policy(self):

        manifest = self._load_json(
            self.manifest_path
        )

        policy = (
            manifest.get(
                "evidence_policy",
                {},
            )
            if manifest
            else {}
        )

        expected = {
            "canonical_evidence_mutated": False,
            "unsupported_claims_promoted": False,
            "fabricated_references_added": False,
        }

        mismatches = []

        for key, value in expected.items():

            if policy.get(key) != value:

                mismatches.append(
                    {
                        "key": key,
                        "expected": value,
                        "actual": policy.get(
                            key
                        ),
                    }
                )

        return {
            "status": (
                "PASS"
                if not mismatches
                else "FAIL"
            ),
            "mismatches": mismatches,
        }

    # =========================================================
    # BUILD REPORT
    # =========================================================

    def audit(self):

        checks = {

            "package_completeness":
                self._check_package_completeness(),

            "manifest_integrity":
                self._check_manifest(),

            "file_path_integrity":
                self._check_file_paths(),

            "numeric_consistency":
                self._check_numeric_consistency(),

            "claim_safety":
                self._check_claim_safety(),

            "latex_integrity":
                self._check_latex_integrity(),

            "evidence_integrity":
                self._check_evidence_integrity(),

            "evidence_policy":
                self._check_evidence_policy(),
        }

        overall_status = (
            "PASS"
            if all(
                check.get(
                    "status"
                ) == "PASS"
                for check in checks.values()
            )
            else "FAIL"
        )

        report = {

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "overall_status":
                overall_status,

            "checks":
                checks,

            "evidence": {

                "submission_package":
                    str(
                        self.submission_dir
                    ),

                "evaluation_summary":
                    str(
                        self.summary_path
                    ),

                "claim_audit":
                    str(
                        self.claim_audit_path
                    ),

                "consistency_audit":
                    str(
                        self.consistency_audit_path
                    ),
            },
        }

        json_path = (
            self.output_dir
            / "submission_quality_report.json"
        )

        markdown_path = (
            self.output_dir
            / "submission_quality_report.md"
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

        self._write_markdown_report(
            report,
            markdown_path,
        )

        return {
            "json": str(
                json_path
            ),
            "markdown": str(
                markdown_path
            ),
            "overall_status":
                overall_status,
            "status":
                "completed",
        }

    # =========================================================
    # MARKDOWN REPORT
    # =========================================================

    def _write_markdown_report(
        self,
        report,
        path,
    ):

        lines = []

        lines.append(
            "# CRME Submission Quality Report"
        )

        lines.append("")

        lines.append(
            f"**Generated:** "
            f"{report['created_at']}"
        )

        lines.append("")

        lines.append(
            f"**Overall Status:** "
            f"`{report['overall_status']}`"
        )

        lines.append("")

        lines.append(
            "## Quality Gate Checks"
        )

        lines.append("")

        lines.append(
            "| Check | Status |"
        )

        lines.append(
            "|---|---|"
        )

        for name, check in report[
            "checks"
        ].items():

            lines.append(
                f"| {name} | "
                f"`{check.get('status')}` |"
            )

        lines.append("")

        lines.append(
            "## Interpretation"
        )

        lines.append("")

        if (
            report["overall_status"]
            == "PASS"
        ):

            lines.append(
                "The CRME submission package "
                "passed all mandatory quality "
                "checks."
            )

        else:

            lines.append(
                "The CRME submission package "
                "failed one or more mandatory "
                "quality checks. The failed "
                "checks should be resolved "
                "before submission."
            )

        lines.append("")

        lines.append(
            "## Evidence Safety"
        )

        lines.append("")

        lines.append(
            "Canonical evaluation evidence "
            "must remain immutable, and "
            "unsupported claims must not be "
            "promoted to established findings."
        )

        lines.append("")

        lines.append(
            "## Reproducibility"
        )

        lines.append("")

        lines.append(
            "The submission quality gate validates "
            "the relationship between the final "
            "manuscript, canonical evaluation "
            "evidence, claim audit artifacts, "
            "consistency audits, tables, figures, "
            "and submission metadata."
        )

        path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )


if __name__ == "__main__":

    result = SubmissionQualityGate().audit()

    print(result)
