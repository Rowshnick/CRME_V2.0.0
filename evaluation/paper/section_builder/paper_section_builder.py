import json
import os
from datetime import datetime, timezone


class PaperSectionBuilder:

    def __init__(
        self,
        summary_json=(
            "evaluation/results/final/"
            "evaluation_summary.json"
        ),
        claim_audit_json=(
            "evaluation/results/final/paper/"
            "claim_audit/"
            "claim_evidence_matrix.json"
        ),
        consistency_json=(
            "evaluation/results/final/paper/"
            "consistency_audit/"
            "q1_consistency_audit.json"
        ),
        output_dir=(
            "evaluation/results/final/paper/"
            "sections"
        ),
    ):
        self.summary_json = summary_json
        self.claim_audit_json = claim_audit_json
        self.consistency_json = consistency_json
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

    def _load_evidence(self):
        return {
            "summary": self._load_json(
                self.summary_json
            ),
            "claims": self._load_json(
                self.claim_audit_json
            ),
            "consistency": self._load_json(
                self.consistency_json
            ),
        }

    def _build_results(self, evidence):
        summary = evidence["summary"]

        metrics = (
            summary
            .get("statistics", {})
            .get("baseline_metrics", {})
        )

        lines = [
            "# Results",
            "",
            (
                "The CRME evaluation pipeline was "
                "conducted across two datasets using "
                "five evaluation metrics."
            ),
            "",
            (
                "The comparative evaluation identified "
                "SRCB_v1 as the best-performing dataset "
                "across all reported metrics."
            ),
            "",
        ]

        for metric, value in metrics.items():
            lines.append(
                f"- **{metric.upper()}**: {value}"
            )

        lines.extend(
            [
                "",
                (
                    "These measurements establish the "
                    "baseline performance profile used "
                    "for subsequent component-level "
                    "ablation analysis."
                ),
            ]
        )

        return "\n".join(lines)

    def _build_ablation(self, evidence):
        ranking = (
            evidence["summary"]
            .get("statistics", {})
            .get("component_ranking", [])
        )

        lines = [
            "# Ablation Study",
            "",
            (
                "The ablation analysis evaluated the "
                "contribution of four architectural "
                "components under five configurations."
            ),
            "",
            (
                "The decisions component exhibited the "
                "largest aggregate degradation, followed "
                "by relations, sessions, and artifacts."
            ),
            "",
            "## Component Ranking",
            "",
        ]

        for item in ranking:
            lines.append(
                f"{item['contribution_rank']}. "
                f"**{item['component']}** — "
                f"aggregate degradation of "
                f"{item['total_degradation']}"
            )

        lines.extend(
            [
                "",
                (
                    "These results support comparative "
                    "component contribution analysis. "
                    "They should not be interpreted as "
                    "definitive causal estimates of "
                    "architectural importance."
                ),
            ]
        )

        return "\n".join(lines)

    def _build_statistics(self, evidence):
        metrics = (
            evidence["summary"]
            .get("statistics", {})
            .get("baseline_metrics", {})
        )

        lines = [
            "# Statistical Analysis",
            "",
            (
                "The current evaluation package reports "
                "descriptive baseline metrics and "
                "component-level degradation values."
            ),
            "",
        ]

        for metric, value in metrics.items():
            lines.append(
                f"- **{metric.upper()}**: {value}"
            )

        lines.extend(
            [
                "",
                (
                    "No inferential statistical test, "
                    "confidence interval, or hypothesis "
                    "test is currently included in the "
                    "evidence package."
                ),
                "",
                (
                    "Accordingly, the present results "
                    "should be interpreted as descriptive "
                    "and comparative rather than as "
                    "statistically significant evidence "
                    "of superiority over a baseline."
                ),
            ]
        )

        return "\n".join(lines)

    def _build_threats(self, evidence):
        return "\n".join(
            [
                "# Threats to Validity",
                "",
                (
                    "Several limitations should be "
                    "considered when interpreting the "
                    "reported findings."
                ),
                "",
                (
                    "First, the current evidence package "
                    "does not include inferential "
                    "statistical testing or confidence "
                    "interval estimation."
                ),
                "",
                (
                    "Second, the ablation results provide "
                    "comparative evidence of component "
                    "contribution but do not establish "
                    "definitive causal importance."
                ),
                "",
                (
                    "Third, the reported evaluation is "
                    "based on the currently available "
                    "datasets and evaluation configurations. "
                    "Generalization to other datasets and "
                    "research workflows requires further "
                    "validation."
                ),
            ]
        )

    def _build_reproducibility(self, evidence):
        consistency = evidence["consistency"]

        status = consistency.get(
            "overall_status",
            "UNKNOWN",
        )

        return "\n".join(
            [
                "# Reproducibility",
                "",
                (
                    "All reported results are derived "
                    "from stored CRME evaluation artifacts."
                ),
                "",
                (
                    "The evaluation pipeline preserves "
                    "the relationship between raw evidence, "
                    "aggregated summaries, paper tables, "
                    "figures, and claim-level evidence."
                ),
                "",
                (
                    f"The Q1 consistency audit completed "
                    f"with overall status `{status}`."
                ),
                "",
                (
                    "Raw evaluation outputs are preserved "
                    "and are not modified by the paper "
                    "generation layer."
                ),
            ]
        )

    def _build_discussion(self, evidence):
        ranking = (
            evidence["summary"]
            .get("statistics", {})
            .get("component_ranking", [])
        )

        top = ranking[0] if ranking else None
        bottom = ranking[-1] if ranking else None

        lines = [
            "# Evidence-Backed Discussion",
            "",
        ]

        if top:
            lines.append(
                (
                    f"The largest observed aggregate "
                    f"degradation was associated with the "
                    f"**{top['component']}** component "
                    f"({top['total_degradation']})."
                )
            )

        lines.append("")

        if bottom:
            lines.append(
                (
                    f"The lowest observed aggregate "
                    f"degradation was associated with the "
                    f"**{bottom['component']}** component "
                    f"({bottom['total_degradation']})."
                )
            )

        lines.extend(
            [
                "",
                (
                    "Together, these results indicate "
                    "heterogeneous component contribution "
                    "within the evaluated CRME architecture."
                ),
                "",
                (
                    "However, the observed ranking should "
                    "be interpreted as an empirical "
                    "comparative result rather than a "
                    "definitive causal decomposition."
                ),
            ]
        )

        return "\n".join(lines)

    def build(self):
        evidence = self._load_evidence()

        sections = {
            "results": self._build_results(
                evidence
            ),
            "ablation": self._build_ablation(
                evidence
            ),
            "statistics": self._build_statistics(
                evidence
            ),
            "threats_to_validity": (
                self._build_threats(evidence)
            ),
            "reproducibility": (
                self._build_reproducibility(evidence)
            ),
            "discussion": self._build_discussion(
                evidence
            ),
        }

        generated_files = {}

        for name, content in sections.items():
            path = os.path.join(
                self.output_dir,
                f"{name}.md",
            )

            with open(
                path,
                "w",
                encoding="utf-8",
            ) as file:
                file.write(content)

            generated_files[name] = path

        manifest = {
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "builder": (
                "PaperSectionBuilder"
            ),
            "sections": generated_files,
            "evidence_sources": {
                "summary": self.summary_json,
                "claim_audit": (
                    self.claim_audit_json
                ),
                "consistency_audit": (
                    self.consistency_json
                ),
            },
            "status": "completed",
        }

        manifest_path = os.path.join(
            self.output_dir,
            "section_manifest.json",
        )

        with open(
            manifest_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                manifest,
                file,
                indent=4,
            )

        return {
            "sections": generated_files,
            "manifest": manifest_path,
            "output_dir": self.output_dir,
            "status": "completed",
        }
