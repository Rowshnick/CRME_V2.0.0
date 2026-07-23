import json
import re
from datetime import datetime, timezone
from pathlib import Path


class FinalManuscriptQualityGate:

    def __init__(self, base_path="."):
        self.base_path = Path(base_path)

        self.summary_path = (
            self.base_path
            / "evaluation/results/final/evaluation_summary.json"
        )

        self.claim_audit_path = (
            self.base_path
            / "evaluation/results/final/paper/claim_audit/"
            / "claim_evidence_matrix.json"
        )

        self.consistency_audit_path = (
            self.base_path
            / "evaluation/results/final/paper/consistency_audit/"
            / "q1_consistency_audit.json"
        )

        self.manuscript_dir = (
            self.base_path
            / "evaluation/results/final/manuscript"
        )

        self.markdown_path = (
            self.manuscript_dir
            / "CRME_MANUSCRIPT.md"
        )

        self.latex_path = (
            self.manuscript_dir
            / "CRME_MANUSCRIPT.tex"
        )

        self.manifest_path = (
            self.manuscript_dir
            / "manuscript_manifest.json"
        )

        self.output_dir = (
            self.manuscript_dir
            / "quality_gate"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =========================================================
    # LOADERS
    # =========================================================

    def _load_json(self, path):

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    # =========================================================
    # SECTION COMPLETENESS
    # =========================================================

    def _check_section_completeness(
        self,
        markdown_text,
        latex_text,
    ):

        required_sections = [
            "Abstract",
            "Introduction",
            "Evaluation Design",
            "Results",
            "Ablation Study",
            "Statistical Analysis",
            "Discussion",
            "Threats to Validity",
            "Reproducibility",
        ]

        markdown_sections = re.findall(
            r"^#{1,3}\s+(.+?)\s*$",
            markdown_text,
            re.MULTILINE,
        )

        latex_sections = re.findall(
            r"\\section\{([^}]+)\}",
            latex_text,
        )

        normalized_markdown = [
            re.sub(
                r"^\d+\.\s*",
                "",
                section,
            ).strip()
            for section in markdown_sections
        ]

        normalized_latex = [
            section.strip()
            for section in latex_sections
        ]

        missing_sections = []

        for required in required_sections:

            found = (
                required in normalized_markdown
                or required in normalized_latex
            )

            if not found:
                missing_sections.append(required)

        return {
            "status": (
                "PASS"
                if not missing_sections
                else "FAIL"
            ),
            "required_sections": required_sections,
            "missing_sections": missing_sections,
            "markdown_sections": markdown_sections,
            "latex_sections": latex_sections,
        }

    # =========================================================
    # EVIDENCE CONSISTENCY
    # =========================================================

    def _check_evidence_consistency(
        self,
        summary,
        consistency,
    ):

        checks = []

        consistency_status = (
            consistency.get(
                "overall_status"
            )
        )

        checks.append(
            {
                "check": "q1_consistency_audit",
                "status": (
                    "PASS"
                    if consistency_status == "PASS"
                    else "FAIL"
                ),
                "value": consistency_status,
            }
        )

        experiment_status = (
            summary
            .get("experiment", {})
            .get("status")
        )

        comparison_status = (
            summary
            .get("comparison", {})
            .get("status")
        )

        statistics_status = (
            summary
            .get("statistics", {})
            .get("status")
        )

        checks.extend(
            [
                {
                    "check": "experiment_status",
                    "status": (
                        "PASS"
                        if experiment_status == "completed"
                        else "FAIL"
                    ),
                    "value": experiment_status,
                },
                {
                    "check": "comparison_status",
                    "status": (
                        "PASS"
                        if comparison_status == "completed"
                        else "FAIL"
                    ),
                    "value": comparison_status,
                },
                {
                    "check": "statistics_status",
                    "status": (
                        "PASS"
                        if statistics_status == "completed"
                        else "FAIL"
                    ),
                    "value": statistics_status,
                },
            ]
        )

        overall = (
            "PASS"
            if all(
                item["status"] == "PASS"
                for item in checks
            )
            else "FAIL"
        )

        return {
            "status": overall,
            "checks": checks,
        }

    # =========================================================
    # NUMERIC CONSISTENCY
    # =========================================================

    def _check_numeric_consistency(
        self,
        summary,
        markdown_text,
        latex_text,
    ):

        expected = (
            summary
            .get("statistics", {})
            .get("baseline_metrics", {})
        )

        combined_text = (
            markdown_text
            + "\n"
            + latex_text
        )

        extracted = {}

        for metric in [
            "MCS",
            "SRS",
            "KGQ",
            "RRS",
            "CES",
        ]:

            pattern = re.compile(
                rf"\*{{0,2}}\s*"
                rf"{re.escape(metric)}"
                rf"\s*\*{{0,2}}"
                rf"\s*[:&]\s*"
                rf"([0-9]+(?:\.[0-9]+)?)",
                re.IGNORECASE,
            )

            match = pattern.search(
                combined_text
            )

            if match:

                extracted[
                    metric
                ] = float(
                    match.group(1)
                )

        mismatches = []

        for metric, expected_value in expected.items():

            metric_upper = metric.upper()

            actual_value = extracted.get(
                metric_upper
            )

            if actual_value is None:

                mismatches.append(
                    {
                        "metric": metric_upper,
                        "expected": expected_value,
                        "actual": None,
                    }
                )

                continue

            if abs(
                float(expected_value)
                - float(actual_value)
            ) > 0.001:

                mismatches.append(
                    {
                        "metric": metric_upper,
                        "expected": expected_value,
                        "actual": actual_value,
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
    # COMPONENT RANKING
    # =========================================================

    def _check_component_ranking(
        self,
        summary,
    ):

        ranking = (
            summary
            .get("statistics", {})
            .get("component_ranking", [])
        )

        expected_order = [
            item["component"]
            for item in ranking
        ]

        expected_values = [
            item["total_degradation"]
            for item in ranking
        ]

        missing_components = []

        required_components = [
            "decisions",
            "relations",
            "sessions",
            "artifacts",
        ]

        for component in required_components:

            if component not in expected_order:

                missing_components.append(
                    component
                )

        descending_order = (
            expected_values
            == sorted(
                expected_values,
                reverse=True,
            )
        )

        status = (
            "PASS"
            if (
                not missing_components
                and descending_order
            )
            else "FAIL"
        )

        return {
            "status": status,
            "expected_order": expected_order,
            "expected_values": expected_values,
            "missing_components": missing_components,
            "descending_order": descending_order,
        }

    # =========================================================
    # CLAIM SAFETY
    # =========================================================

    def _check_claim_safety(
        self,
        claim_audit,
    ):

        unsafe_claims = []

        for claim in claim_audit.get(
            "claims",
            [],
        ):

            status = claim.get(
                "status"
            )

            if status in [
                "NOT_ESTABLISHED",
                "LIMITED",
            ]:

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

    def _check_latex_integrity(
        self,
        latex_text,
    ):

        checks = []

        document_start = (
            latex_text.lstrip()
            .startswith(
                "\\documentclass"
            )
        )

        checks.append(
            {
                "check": "document_start",
                "status": (
                    "PASS"
                    if document_start
                    else "FAIL"
                ),
            }
        )

        document_end = (
            "\\end{document}"
            in latex_text
        )

        checks.append(
            {
                "check": "document_end",
                "status": (
                    "PASS"
                    if document_end
                    else "FAIL"
                ),
            }
        )

        tokens = re.findall(
            r"\\(begin|end)\{([^}]+)\}",
            latex_text,
        )

        stack = []

        structural_errors = []

        for token_type, env_name in tokens:

            if token_type == "begin":

                stack.append(
                    env_name
                )

            else:

                if not stack:

                    structural_errors.append(
                        "unexpected end "
                        f"of {env_name}"
                    )

                    continue

                expected_env = stack.pop()

                if expected_env != env_name:

                    structural_errors.append(
                        "environment nesting "
                        "mismatch: expected "
                        f"end of {expected_env}, "
                        f"found end of {env_name}"
                    )

        if stack:

            structural_errors.append(
                "unclosed environments: "
                + ", ".join(stack)
            )

        checks.append(
            {
                "check": "environment_balance",
                "status": (
                    "PASS"
                    if not structural_errors
                    else "FAIL"
                ),
                "structural_errors": structural_errors,
                "token_count": len(tokens),
            }
        )

        required_commands = [
            "\\documentclass",
            "\\begin{document}",
            "\\end{document}",
        ]

        missing_commands = [
            command
            for command in required_commands
            if command not in latex_text
        ]

        checks.append(
            {
                "check": "required_commands",
                "status": (
                    "PASS"
                    if not missing_commands
                    else "FAIL"
                ),
                "missing_commands": missing_commands,
            }
        )

        overall = (
            "PASS"
            if all(
                item["status"] == "PASS"
                for item in checks
            )
            else "FAIL"
        )

        return {
            "status": overall,
            "checks": checks,
        }

    # =========================================================
    # REPRODUCIBILITY
    # =========================================================

    def _check_reproducibility(
        self,
        markdown_text,
        latex_text,
        manifest,
    ):

        required_phrase = (
            "stored CRME evaluation artifacts"
        )

        found_in_markdown = (
            required_phrase
            in markdown_text
        )

        found_in_latex = (
            required_phrase
            in latex_text
        )

        manifest_valid = isinstance(
            manifest,
            dict,
        )

        status = (
            "PASS"
            if (
                found_in_markdown
                and found_in_latex
                and manifest_valid
            )
            else "FAIL"
        )

        return {
            "status": status,
            "missing_phrases": (
                []
                if (
                    found_in_markdown
                    and found_in_latex
                )
                else [required_phrase]
            ),
            "manifest_valid": manifest_valid,
            "found_in_markdown": found_in_markdown,
            "found_in_latex": found_in_latex,
        }

    # =========================================================
    # MANIFEST INTEGRITY
    # =========================================================

    def _check_manifest_integrity(
        self,
        manifest,
    ):

        required_keys = [
            "manuscript_type",
            "outputs",
            "sections",
            "sources",
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
        }

    # =========================================================
    # AUDIT
    # =========================================================

    def audit(self):

        summary = self._load_json(
            self.summary_path
        )

        claim_audit = self._load_json(
            self.claim_audit_path
        )

        consistency = self._load_json(
            self.consistency_audit_path
        )

        manifest = self._load_json(
            self.manifest_path
        )

        markdown_text = (
            self.markdown_path
            .read_text(
                encoding="utf-8"
            )
        )

        latex_text = (
            self.latex_path
            .read_text(
                encoding="utf-8"
            )
        )

        checks = {
            "section_completeness":
                self._check_section_completeness(
                    markdown_text,
                    latex_text,
                ),

            "evidence_consistency":
                self._check_evidence_consistency(
                    summary,
                    consistency,
                ),

            "numeric_consistency":
                self._check_numeric_consistency(
                    summary,
                    markdown_text,
                    latex_text,
                ),

            "component_ranking":
                self._check_component_ranking(
                    summary,
                ),

            "claim_safety":
                self._check_claim_safety(
                    claim_audit,
                ),

            "latex_integrity":
                self._check_latex_integrity(
                    latex_text,
                ),

            "reproducibility":
                self._check_reproducibility(
                    markdown_text,
                    latex_text,
                    manifest,
                ),

            "manifest_integrity":
                self._check_manifest_integrity(
                    manifest,
                ),
        }

        overall_status = (
            "PASS"
            if all(
                check["status"] == "PASS"
                for check in checks.values()
            )
            else "FAIL"
        )

        report = {
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "overall_status":
                overall_status,

            "checks":
                checks,

            "evidence": {
                "summary":
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

                "manuscript_markdown":
                    str(
                        self.markdown_path
                    ),

                "manuscript_latex":
                    str(
                        self.latex_path
                    ),

                "manuscript_manifest":
                    str(
                        self.manifest_path
                    ),
            },
        }

        json_path = (
            self.output_dir
            / "final_quality_report.json"
        )

        markdown_path = (
            self.output_dir
            / "final_quality_report.md"
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
            "json": str(json_path),
            "markdown": str(markdown_path),
            "output_dir": str(
                self.output_dir
            ),
            "status": "completed",
        }

    # =========================================================
    # REPORT
    # =========================================================

    def _write_markdown_report(
        self,
        report,
        path,
    ):

        lines = [
            "# CRME Final Manuscript Quality Report",
            "",
            f"**Generated:** "
            f"{report['created_at']}",
            "",
            f"**Overall Status:** "
            f"`{report['overall_status']}`",
            "",
            "## Quality Gate Checks",
            "",
            "| Check | Status |",
            "|---|---|",
        ]

        for name, result in report[
            "checks"
        ].items():

            lines.append(
                f"| {name} | "
                f"`{result['status']}` |"
            )

        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                (
                    "The quality gate validates "
                    "the relationship between "
                    "canonical evaluation evidence, "
                    "claim audit artifacts, "
                    "manuscript content, and "
                    "reproducibility metadata."
                ),
                "",
            ]
        )

        path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )


if __name__ == "__main__":

    result = (
        FinalManuscriptQualityGate()
        .audit()
    )

    print(result)
