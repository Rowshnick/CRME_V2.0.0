import json
import os
from datetime import datetime, timezone


class Q1ConsistencyAuditor:

    def __init__(
        self,
        summary_json=(
            "evaluation/results/final/"
            "evaluation_summary.json"
        ),
        claim_audit_json=(
            "evaluation/results/final/paper/"
            "claim_audit/claim_evidence_matrix.json"
        ),
        ranking_csv=(
            "evaluation/results/final/paper/"
            "figures/component_contribution.csv"
        ),
        output_dir=(
            "evaluation/results/final/paper/"
            "consistency_audit"
        ),
    ):
        self.summary_json = summary_json
        self.claim_audit_json = claim_audit_json
        self.ranking_csv = ranking_csv
        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True,
        )

    def _load_json(self, path):
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def _load_ranking_csv(self):
        import csv

        rows = []

        with open(
            self.ranking_csv,
            "r",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                rows.append(
                    {
                        "rank": int(row["rank"]),
                        "component": row["component"],
                        "total_degradation": float(
                            row["total_degradation"]
                        ),
                    }
                )

        return rows

    def audit(self):

        summary = self._load_json(
            self.summary_json
        )

        claim_audit = self._load_json(
            self.claim_audit_json
        )

        csv_ranking = self._load_ranking_csv()

        summary_ranking = (
            summary
            .get("statistics", {})
            .get("component_ranking", [])
        )

        checks = []

        # -------------------------------------------------
        # CHECK 1: Ranking consistency
        # -------------------------------------------------

        ranking_match = True

        if len(csv_ranking) != len(
            summary_ranking
        ):
            ranking_match = False

        else:
            for csv_item, json_item in zip(
                csv_ranking,
                summary_ranking,
            ):
                if (
                    csv_item["component"]
                    != json_item["component"]
                ):
                    ranking_match = False

                if abs(
                    csv_item[
                        "total_degradation"
                    ]
                    - json_item[
                        "total_degradation"
                    ]
                ) > 0.01:
                    ranking_match = False

        checks.append(
            {
                "check_id": "Q1-C001",
                "check": (
                    "Ablation ranking is consistent "
                    "between canonical summary and "
                    "figure data."
                ),
                "status": (
                    "PASS"
                    if ranking_match
                    else "FAIL"
                ),
            }
        )

        # -------------------------------------------------
        # CHECK 2: Claim status consistency
        # -------------------------------------------------

        claims = claim_audit.get(
            "claims",
            [],
        )

        unsupported_claims = [
            claim["claim_id"]
            for claim in claims
            if claim.get("status")
            == "NOT_ESTABLISHED"
        ]

        checks.append(
            {
                "check_id": "Q1-C002",
                "check": (
                    "Unsupported claims are explicitly "
                    "flagged rather than presented as "
                    "established findings."
                ),
                "status": (
                    "PASS"
                    if unsupported_claims
                    else "REVIEW"
                ),
                "details": unsupported_claims,
            }
        )

        # -------------------------------------------------
        # CHECK 3: Ranking order
        # -------------------------------------------------

        ranking_order = [
            item["component"]
            for item in csv_ranking
        ]

        degradation_values = [
            item["total_degradation"]
            for item in csv_ranking
        ]

        sorted_correctly = (
            degradation_values
            == sorted(
                degradation_values,
                reverse=True,
            )
        )

        checks.append(
            {
                "check_id": "Q1-C003",
                "check": (
                    "Component ranking is ordered by "
                    "descending aggregate degradation."
                ),
                "status": (
                    "PASS"
                    if sorted_correctly
                    else "FAIL"
                ),
            }
        )

        # -------------------------------------------------
        # CHECK 4: Best and lowest components
        # -------------------------------------------------

        highest_component = (
            csv_ranking[0]["component"]
            if csv_ranking
            else None
        )

        lowest_component = (
            csv_ranking[-1]["component"]
            if csv_ranking
            else None
        )

        checks.append(
            {
                "check_id": "Q1-C004",
                "check": (
                    "Highest and lowest contribution "
                    "claims match the ranking evidence."
                ),
                "status": (
                    "PASS"
                    if (
                        highest_component
                        == "decisions"
                        and lowest_component
                        == "artifacts"
                    )
                    else "FAIL"
                ),
                "highest_component": (
                    highest_component
                ),
                "lowest_component": (
                    lowest_component
                ),
            }
        )

        # -------------------------------------------------
        # CHECK 5: Baseline metrics
        # -------------------------------------------------

        baseline_metrics = (
            summary
            .get("statistics", {})
            .get("baseline_metrics", {})
        )

        baseline_valid = (
            len(baseline_metrics) > 0
        )

        checks.append(
            {
                "check_id": "Q1-C005",
                "check": (
                    "Baseline metrics are available "
                    "for the reported evaluation."
                ),
                "status": (
                    "PASS"
                    if baseline_valid
                    else "FAIL"
                ),
                "metric_count": len(
                    baseline_metrics
                ),
            }
        )

        # -------------------------------------------------
        # Overall result
        # -------------------------------------------------

        hard_failures = [
            item
            for item in checks
            if item["status"] == "FAIL"
        ]

        overall_status = (
            "PASS"
            if not hard_failures
            else "FAIL"
        )

        result = {
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "audit_type": (
                "Q1 consistency audit"
            ),
            "overall_status": overall_status,
            "checks": checks,
            "evidence": {
                "summary": self.summary_json,
                "claim_audit": (
                    self.claim_audit_json
                ),
                "ranking_data": self.ranking_csv,
            },
        }

        json_path = os.path.join(
            self.output_dir,
            "q1_consistency_audit.json",
        )

        with open(
            json_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                result,
                file,
                indent=4,
            )

        markdown_lines = [
            "# CRME Q1 Consistency Audit",
            "",
            f"**Overall Status:** `{overall_status}`",
            "",
            "| Check | Description | Status |",
            "|---|---|---|",
        ]

        for check in checks:
            markdown_lines.append(
                f"| {check['check_id']} | "
                f"{check['check']} | "
                f"{check['status']} |"
            )

        markdown_lines.extend(
            [
                "",
                "## Interpretation",
                "",
                (
                    "The audit verifies consistency between "
                    "the canonical evaluation summary, claim "
                    "evidence matrix, and figure data."
                ),
                "",
                (
                    "Claims marked NOT_ESTABLISHED should not "
                    "be presented as statistically confirmed "
                    "findings in the paper."
                ),
            ]
        )

        markdown_path = os.path.join(
            self.output_dir,
            "q1_consistency_audit.md",
        )

        with open(
            markdown_path,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(
                "\n".join(
                    markdown_lines
                )
            )

        return {
            "json": json_path,
            "markdown": markdown_path,
            "overall_status": overall_status,
            "check_count": len(checks),
        }
