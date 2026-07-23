import os
import json


class AblationVisualizer:

    def __init__(
        self,
        output_dir="evaluation/results/ablations/figures"
    ):

        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    def load_report(
        self,
        path
    ):

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def generate_csv(
        self,
        report
    ):

        path = os.path.join(
            self.output_dir,
            "ablation_metrics.csv"
        )

        results = report.get(
            "results",
            []
        )

        metrics = [
            "mcs",
            "srs",
            "kgq",
            "rrs",
            "ces"
        ]

        lines = []

        lines.append(
            "configuration,"
            + ",".join(metrics)
        )

        for result in results:

            configuration = result.get(
                "configuration",
                "UNKNOWN"
            )

            values = []

            result_metrics = result.get(
                "metrics",
                {}
            )

            for metric in metrics:

                values.append(
                    str(
                        result_metrics.get(
                            metric,
                            0
                        )
                    )
                )

            lines.append(
                configuration
                + ","
                + ",".join(values)
            )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "\n".join(
                    lines
                )
            )

        return path

    def generate_degradation_csv(
        self,
        report
    ):

        path = os.path.join(
            self.output_dir,
            "ablation_degradation.csv"
        )

        absolute = report.get(
            "analysis",
            {}
        ).get(
            "absolute_degradation",
            {}
        )

        metrics = [
            "mcs",
            "srs",
            "kgq",
            "rrs",
            "ces"
        ]

        lines = []

        lines.append(
            "configuration,"
            + ",".join(metrics)
        )

        for configuration, values in absolute.items():

            row = [
                configuration
            ]

            for metric in metrics:

                row.append(
                    str(
                        values.get(
                            metric,
                            0
                        )
                    )
                )

            lines.append(
                ",".join(
                    row
                )
            )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "\n".join(
                    lines
                )
            )

        return path

    def generate_mermaid(
        self,
        report
    ):

        path = os.path.join(
            self.output_dir,
            "ablation_chart.md"
        )

        results = report.get(
            "results",
            []
        )

        lines = []

        lines.append(
            "```mermaid"
        )

        lines.append(
            "xychart-beta"
        )

        lines.append(
            '    title "CRME Ablation Study - CES"'
        )

        lines.append(
            '    x-axis ["FULL", "NO_REL", "NO_SESS", "NO_DEC", "NO_ART"]'
        )

        ces_values = []

        for result in results:

            ces_values.append(
                str(
                    result.get(
                        "metrics",
                        {}
                    ).get(
                        "ces",
                        0
                    )
                )
            )

        lines.append(
            "    y-axis \"CES\" 0 --> 100"
        )

        lines.append(
            "    bar ["
            + ", ".join(
                ces_values
            )
            + "]"
        )

        lines.append(
            "```"
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "\n".join(
                    lines
                )
            )

        return path

    def generate_all(
        self,
        report_path
    ):

        report = self.load_report(
            report_path
        )

        csv_metrics = self.generate_csv(
            report
        )

        csv_degradation = (
            self.generate_degradation_csv(
                report
            )
        )

        mermaid = self.generate_mermaid(
            report
        )

        return {

            "metrics_csv":
                csv_metrics,

            "degradation_csv":
                csv_degradation,

            "mermaid":
                mermaid
        }

