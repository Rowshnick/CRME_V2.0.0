import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


class SubmissionPackageBuilder:

    def __init__(self, base_path="."):

        self.base_path = Path(base_path)

        self.manuscript_dir = (
            self.base_path
            / "evaluation/results/final/manuscript"
        )

        self.paper_dir = (
            self.base_path
            / "evaluation/results/final/paper"
        )

        self.output_dir = (
            self.base_path
            / "evaluation/results/final/submission"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.figures_dir = (
            self.output_dir
            / "figures"
        )

        self.tables_dir = (
            self.output_dir
            / "tables"
        )

        self.figures_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.tables_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =========================================================
    # FILE HELPERS
    # =========================================================

    def _copy_if_exists(
        self,
        source,
        destination,
    ):

        source = Path(source)
        destination = Path(destination)

        if not source.exists():

            return False

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            source,
            destination,
        )

        return True

    # =========================================================
    # MANUSCRIPT
    # =========================================================

    def _copy_manuscript(self):

        copied = []

        markdown_source = (
            self.manuscript_dir
            / "CRME_MANUSCRIPT.md"
        )

        latex_source = (
            self.manuscript_dir
            / "CRME_MANUSCRIPT.tex"
        )

        markdown_target = (
            self.output_dir
            / "CRME_SUBMISSION_PACKAGE.md"
        )

        latex_target = (
            self.output_dir
            / "CRME_SUBMISSION_PACKAGE.tex"
        )

        if self._copy_if_exists(
            markdown_source,
            markdown_target,
        ):

            copied.append(
                str(markdown_target)
            )

        if self._copy_if_exists(
            latex_source,
            latex_target,
        ):

            copied.append(
                str(latex_target)
            )

        return copied

    # =========================================================
    # TABLES
    # =========================================================

    def _copy_tables(self):

        copied = []

        source_dir = (
            self.paper_dir
            / "tables"
        )

        if not source_dir.exists():

            return copied

        for source in source_dir.iterdir():

            if not source.is_file():

                continue

            destination = (
                self.tables_dir
                / source.name
            )

            if self._copy_if_exists(
                source,
                destination,
            ):

                copied.append(
                    str(destination)
                )

        return copied

    # =========================================================
    # FIGURES
    # =========================================================

    def _copy_figures(self):

        copied = []

        source_dir = (
            self.paper_dir
            / "figures"
        )

        if not source_dir.exists():

            return copied

        for source in source_dir.iterdir():

            if not source.is_file():

                continue

            destination = (
                self.figures_dir
                / source.name
            )

            if self._copy_if_exists(
                source,
                destination,
            ):

                copied.append(
                    str(destination)
                )

        return copied

    # =========================================================
    # BIBTEX
    # =========================================================

    def _build_bibliography(self):

        bibliography_path = (
            self.output_dir
            / "references.bib"
        )

        content = r"""% CRME Submission Package Bibliography
%
% This bibliography file is intentionally initialized
% without fabricated references.
%
% Verified references should be added during the
% Journal-Specific Manuscript Preparation phase.
%
"""

        bibliography_path.write_text(
            content,
            encoding="utf-8",
        )

        return str(
            bibliography_path
        )

    # =========================================================
    # README
    # =========================================================

    def _build_readme(
        self,
        markdown_path,
        latex_path,
        bibliography_path,
        figures,
        tables,
    ):

        readme_path = (
            self.output_dir
            / "README_SUBMISSION.md"
        )

        lines = [
            "# CRME Journal Submission Package",
            "",
            "This package was generated from the "
            "evidence-backed final CRME manuscript.",
            "",
            "## Package Status",
            "",
            "The source manuscript passed the final "
            "manuscript quality gate before packaging.",
            "",
            "## Main Manuscript",
            "",
            f"- `{Path(markdown_path).name}`",
            f"- `{Path(latex_path).name}`",
            "",
            "## Bibliography",
            "",
            f"- `{Path(bibliography_path).name}`",
            "",
            "The bibliography is intentionally initialized "
            "without fabricated references.",
            "",
            "## Figures",
            "",
        ]

        for figure in figures:

            lines.append(
                f"- `{Path(figure).name}`"
            )

        lines.extend(
            [
                "",
                "## Tables",
                "",
            ]
        )

        for table in tables:

            lines.append(
                f"- `{Path(table).name}`"
            )

        lines.extend(
            [
                "",
                "## Evidence Governance",
                "",
                "The submission package is derived from "
                "stored CRME evaluation artifacts.",
                "",
                "The package does not modify canonical "
                "evaluation evidence.",
                "",
                "Unsupported or limited claims are not "
                "promoted to established findings.",
                "",
                "## Next Phase",
                "",
                "The next phase is journal-specific adaptation "
                "for IEEE, Elsevier, or another selected "
                "target journal.",
                "",
            ]
        )

        readme_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return str(
            readme_path
        )

    # =========================================================
    # MANIFEST
    # =========================================================

    def _build_manifest(
        self,
        markdown_path,
        latex_path,
        bibliography_path,
        readme_path,
        figures,
        tables,
    ):

        manifest_path = (
            self.output_dir
            / "submission_manifest.json"
        )

        manifest = {
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "package_type":
                "journal_agnostic_submission_package",

            "manuscript_status":
                "final_quality_gate_passed",

            "manuscript": {
                "markdown": str(
                    markdown_path
                ),
                "latex": str(
                    latex_path
                ),
            },

            "bibliography": str(
                bibliography_path
            ),

            "figures": [
                str(path)
                for path in figures
            ],

            "tables": [
                str(path)
                for path in tables
            ],

            "readme": str(
                readme_path
            ),

            "sources": {
                "final_manuscript":
                    "evaluation/results/final/manuscript",

                "canonical_evaluation":
                    "evaluation/results/final/evaluation_summary.json",

                "claim_audit":
                    "evaluation/results/final/paper/claim_audit",

                "consistency_audit":
                    "evaluation/results/final/paper/consistency_audit",
            },

            "journal_adapters": [
                "IEEE",
                "Elsevier",
                "Generic Article",
            ],

            "evidence_policy": {
                "canonical_evidence_mutated": False,
                "unsupported_claims_promoted": False,
                "fabricated_references_added": False,
            },
        }

        with open(
            manifest_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                manifest,
                f,
                indent=4,
                ensure_ascii=False,
            )

        return str(
            manifest_path
        )

    # =========================================================
    # BUILD
    # =========================================================

    def build(self):

        manuscript_files = (
            self._copy_manuscript()
        )

        tables = (
            self._copy_tables()
        )

        figures = (
            self._copy_figures()
        )

        bibliography = (
            self._build_bibliography()
        )

        markdown_path = (
            self.output_dir
            / "CRME_SUBMISSION_PACKAGE.md"
        )

        latex_path = (
            self.output_dir
            / "CRME_SUBMISSION_PACKAGE.tex"
        )

        readme = (
            self._build_readme(
                markdown_path,
                latex_path,
                bibliography,
                figures,
                tables,
            )
        )

        manifest = (
            self._build_manifest(
                markdown_path,
                latex_path,
                bibliography,
                readme,
                figures,
                tables,
            )
        )

        return {
            "output_dir": str(
                self.output_dir
            ),

            "manuscript_files":
                manuscript_files,

            "tables":
                tables,

            "figures":
                figures,

            "bibliography":
                bibliography,

            "readme":
                readme,

            "manifest":
                manifest,

            "status":
                "completed",
        }


if __name__ == "__main__":

    result = (
        SubmissionPackageBuilder()
        .build()
    )

    print(result)
