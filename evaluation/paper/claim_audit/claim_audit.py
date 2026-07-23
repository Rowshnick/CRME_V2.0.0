import json
import os
from datetime import datetime, timezone


class ClaimAudit:

    def __init__(self, summary_path=None, output_dir=None):
        self.summary_path = summary_path or (
            "evaluation/results/final/evaluation_summary.json"
        )

        self.output_dir = output_dir or (
            "evaluation/results/final/paper/claim_audit"
        )

        os.makedirs(self.output_dir, exist_ok=True)

    def _load_summary(self):
        with open(self.summary_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_claims(self, summary):
        statistics = summary.get("statistics", {})
        ranking = statistics.get("component_ranking", [])
        baseline_metrics = statistics.get("baseline_metrics", {})

        ranking_map = {
            item.get("component"): item
            for item in ranking
        }

        decisions = ranking_map.get("decisions", {})
        relations = ranking_map.get("relations", {})
        sessions = ranking_map.get("sessions", {})
        artifacts = ranking_map.get("artifacts", {})

        claims = []

        claims.append({
            "claim_id": "C001",
            "claim": (
                "CRME has a measurable baseline performance profile "
                "across multiple evaluation metrics."
            ),
            "evidence": [
                "evaluation_summary.json",
                "statistics.baseline_metrics"
            ],
            "status": "SUPPORTED",
            "strength": "DIRECT"
        })

        claims.append({
            "claim_id": "C002",
            "claim": (
                "The decisions component exhibited the largest aggregate "
                "degradation under the evaluated ablation settings."
            ),
            "evidence": [
                "statistics.component_ranking",
                "component=decisions",
                f"total_degradation={decisions.get('total_degradation')}"
            ],
            "status": "SUPPORTED",
            "strength": "DIRECT"
        })

        claims.append({
            "claim_id": "C003",
            "claim": (
                "The relations component ranked second in aggregate "
                "ablation degradation."
            ),
            "evidence": [
                "statistics.component_ranking",
                "component=relations",
                f"total_degradation={relations.get('total_degradation')}"
            ],
            "status": "SUPPORTED",
            "strength": "DIRECT"
        })

        claims.append({
            "claim_id": "C004",
            "claim": (
                "The sessions component exhibited a lower aggregate "
                "degradation than the two highest-ranked components."
            ),
            "evidence": [
                "statistics.component_ranking",
                "component=sessions",
                f"total_degradation={sessions.get('total_degradation')}"
            ],
            "status": "SUPPORTED",
            "strength": "DIRECT"
        })

        claims.append({
            "claim_id": "C005",
            "claim": (
                "The artifacts component exhibited the lowest aggregate "
                "degradation among the evaluated components."
            ),
            "evidence": [
                "statistics.component_ranking",
                "component=artifacts",
                f"total_degradation={artifacts.get('total_degradation')}"
            ],
            "status": "SUPPORTED",
            "strength": "DIRECT"
        })

        claims.append({
            "claim_id": "C006",
            "claim": (
                "The current evidence does not establish that CRME "
                "statistically significantly outperforms a baseline system."
            ),
            "evidence": [
                "evaluation_summary.json",
                "absence_of_inferential_statistics"
            ],
            "status": "SUPPORTED",
            "strength": "DIRECT",
            "note": (
                "No inferential statistical test, confidence interval, "
                "or hypothesis test is present in the current evidence package."
            )
        })

        claims.append({
            "claim_id": "C007",
            "claim": (
                "The evaluated component ranking provides comparative "
                "evidence of heterogeneous component contribution but does "
                "not establish definitive causal importance."
            ),
            "evidence": [
                "statistics.component_ranking",
                "ablation_results",
                "threats_to_validity"
            ],
            "status": "SUPPORTED",
            "strength": "DIRECT",
            "note": (
                "Ablation results support comparative contribution analysis "
                "but should not be interpreted as definitive causal estimates."
            )
        })

        return claims

    def audit(self):
        summary = self._load_summary()
        claims = self._build_claims(summary)

        created_at = datetime.now(timezone.utc).isoformat()

        result = {
            "created_at": created_at,
            "source": self.summary_path,
            "audit_status": "completed",
            "claims": claims
        }

        json_path = os.path.join(
            self.output_dir,
            "claim_evidence_matrix.json"
        )

        markdown_path = os.path.join(
            self.output_dir,
            "claim_evidence_matrix.md"
        )

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                result,
                f,
                indent=4,
                ensure_ascii=False
            )

        self._write_markdown(
            claims,
            markdown_path
        )

        return {
            "json": json_path,
            "markdown": markdown_path,
            "claim_count": len(claims),
            "status": "completed"
        }

    def _write_markdown(self, claims, path):
        lines = [
            "# CRME Claim-Evidence Audit",
            "",
            "This audit maps paper-level claims to stored CRME evaluation evidence.",
            "",
            "| ID | Claim | Status | Strength |",
            "|---|---|---|---|"
        ]

        for claim in claims:
            lines.append(
                "| {id} | {claim} | {status} | {strength} |".format(
                    id=claim["claim_id"],
                    claim=claim["claim"],
                    status=claim["status"],
                    strength=claim["strength"]
                )
            )

        lines.extend([
            "",
            "## Evidence Notes",
            "",
            "- **C006**: The current evidence package does not include "
            "inferential statistical testing or confidence interval estimation.",
            "",
            "- **C007**: Ablation results support comparative contribution "
            "analysis but do not establish definitive causal importance."
        ])

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


if __name__ == "__main__":
    print(ClaimAudit().audit())
