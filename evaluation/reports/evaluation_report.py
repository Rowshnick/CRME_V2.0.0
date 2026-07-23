import json
import os


class EvaluationReport:
    """
    CRME Evaluation Report Layer v1.6-dev

    Converts EvaluationEngine results into:
        - JSON reports
        - Markdown reports
        - compact summaries
    """

    def __init__(
        self,
        output_dir="evaluation/results"
    ):
        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
        evaluation_result
    ):
        metrics = evaluation_result.get(
            "metrics",
            {}
        )

        benchmark = evaluation_result.get(
            "benchmark",
            {}
        )

        return {
            "evaluation_id": evaluation_result.get(
                "evaluation_id"
            ),

            "dataset": evaluation_result.get(
                "dataset"
            ),

            "dataset_type": benchmark.get(
                "dataset_type"
            ),

            "ces": metrics.get(
                "ces",
                0.0
            ),

            "mcs": metrics.get(
                "mcs",
                0.0
            ),

            "srs": metrics.get(
                "srs",
                0.0
            ),

            "kgq": metrics.get(
                "kgq",
                0.0
            ),

            "rrs": metrics.get(
                "rrs",
                0.0
            ),

            "runtime_sec": benchmark.get(
                "runtime_sec",
                0.0
            ),

            "knowledge_nodes": benchmark.get(
                "knowledge_nodes",
                0
            ),

            "relations": benchmark.get(
                "relations",
                0
            ),

            "sessions": benchmark.get(
                "sessions",
                0
            ),

            "memories": benchmark.get(
                "memories",
                0
            ),

            "decisions": benchmark.get(
                "decisions",
                0
            ),

            "artifacts": benchmark.get(
                "artifacts",
                0
            )
        }

    # =====================================================
    # SAVE JSON
    # =====================================================

    def save_json(
        self,
        evaluation_result,
        filename=None
    ):
        if filename is None:
            filename = (
                evaluation_result.get(
                    "evaluation_id",
                    "evaluation"
                )
                + ".json"
            )

        path = os.path.join(
            self.output_dir,
            filename
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                evaluation_result,
                file,
                indent=4
            )

        return path

    # =====================================================
    # GENERATE MARKDOWN
    # =====================================================

    def generate_markdown(
        self,
        evaluation_result
    ):
        summary = self.summary(
            evaluation_result
        )

        benchmark = evaluation_result.get(
            "benchmark",
            {}
        )

        metadata = benchmark.get(
            "metadata",
            {}
        )

        metadata_json = json.dumps(
            metadata,
            indent=4
        )

        lines = []

        lines.append(
            "# CRME Evaluation Report"
        )

        lines.append("")
        lines.append(
            "## Evaluation Metadata"
        )

        lines.append("")
        lines.append(
            "| Field | Value |"
        )

        lines.append(
            "|---|---|"
        )

        lines.append(
            f"| Evaluation ID | {summary['evaluation_id']} |"
        )

        lines.append(
            f"| Dataset | {summary['dataset']} |"
        )

        lines.append(
            f"| Dataset Type | {summary['dataset_type']} |"
        )

        lines.append(
            f"| Engine Version | {metadata.get('version', 'unknown')} |"
        )

        lines.append(
            f"| Execution Version | {metadata.get('execution_version', 'unknown')} |"
        )

        lines.append(
            f"| Status | {evaluation_result.get('status', 'unknown')} |"
        )

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(
            "## Evaluation Metrics"
        )

        lines.append("")
        lines.append(
            "| Metric | Score |"
        )

        lines.append(
            "|---|---:|"
        )

        lines.append(
            f"| MCS | {summary['mcs']:.2f} |"
        )

        lines.append(
            f"| SRS | {summary['srs']:.2f} |"
        )

        lines.append(
            f"| KGQ | {summary['kgq']:.2f} |"
        )

        lines.append(
            f"| RRS | {summary['rrs']:.2f} |"
        )

        lines.append(
            f"| **CES** | **{summary['ces']:.2f}** |"
        )

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(
            "## Benchmark Statistics"
        )

        lines.append("")
        lines.append(
            "| Metric | Value |"
        )

        lines.append(
            "|---|---:|"
        )

        lines.append(
            f"| Runtime (sec) | {summary['runtime_sec']} |"
        )

        lines.append(
            f"| Knowledge Nodes | {summary['knowledge_nodes']} |"
        )

        lines.append(
            f"| Relations | {summary['relations']} |"
        )

        lines.append(
            f"| Sessions | {summary['sessions']} |"
        )

        lines.append(
            f"| Memories | {summary['memories']} |"
        )

        lines.append(
            f"| Decisions | {summary['decisions']} |"
        )

        lines.append(
            f"| Artifacts | {summary['artifacts']} |"
        )

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(
            "## Evaluation Timeline"
        )

        lines.append("")

        lines.append(
            f"- Started: `{evaluation_result.get('started_at')}`"
        )

        lines.append(
            f"- Finished: `{evaluation_result.get('finished_at')}`"
        )

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(
            "## Reproducibility Metadata"
        )

        lines.append("")
        lines.append(
            "```json"
        )

        lines.append(
            metadata_json
        )

        lines.append(
            "```"
        )

        lines.append("")
        lines.append(
            "*Generated by CRME Evaluation Framework v1.6-dev*"
        )

        return "\n".join(
            lines
        )

    # =====================================================
    # SAVE MARKDOWN
    # =====================================================

    def save_markdown(
        self,
        evaluation_result,
        filename=None
    ):
        if filename is None:
            filename = (
                evaluation_result.get(
                    "evaluation_id",
                    "evaluation"
                )
                + ".md"
            )

        path = os.path.join(
            self.output_dir,
            filename
        )

        markdown = self.generate_markdown(
            evaluation_result
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                markdown
            )

        return path

    # =====================================================
    # SAVE ALL
    # =====================================================

    def save_all(
        self,
        evaluation_result
    ):
        return {
            "json": self.save_json(
                evaluation_result
            ),

            "markdown": self.save_markdown(
                evaluation_result
            ),

            "summary": self.summary(
                evaluation_result
            )
        }
