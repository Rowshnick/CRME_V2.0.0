import csv
import os


class AblationLatexTableGenerator:
    """
    Generate LaTeX tables from CRME ablation CSV outputs.
    """

    def __init__(
        self,
        output_dir="evaluation/results/ablations/latex"
    ):
        self.output_dir = output_dir
        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    def _read_csv(self, path):
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            return list(
                csv.DictReader(file)
            )

    def _fmt(self, value):
        try:
            return f"{float(value):.2f}"
        except (
            TypeError,
            ValueError
        ):
            return str(value)

    def generate_metrics_table(
        self,
        metrics_csv
    ):
        rows = self._read_csv(
            metrics_csv
        )

        output_path = os.path.join(
            self.output_dir,
            "ablation_metrics_table.tex"
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "\\begin{table}[htbp]\n"
            )

            file.write(
                "\\centering\n"
            )

            file.write(
                "\\caption{CRME Ablation Study Results}\n"
            )

            file.write(
                "\\label{tab:crme-ablation-metrics}\n"
            )

            file.write(
                "\\begin{tabular}{lccccc}\n"
            )

            file.write(
                "\\toprule\n"
            )

            file.write(
                "Configuration & MCS & SRS & KGQ & RRS & CES \\\\\n"
            )

            file.write(
                "\\midrule\n"
            )

            for row in rows:

                file.write(
                    f"{row['configuration']} & "
                    f"{self._fmt(row['mcs'])} & "
                    f"{self._fmt(row['srs'])} & "
                    f"{self._fmt(row['kgq'])} & "
                    f"{self._fmt(row['rrs'])} & "
                    f"{self._fmt(row['ces'])} \\\\\n"
                )

            file.write(
                "\\bottomrule\n"
            )

            file.write(
                "\\end{tabular}\n"
            )

            file.write(
                "\\end{table}\n"
            )

        return output_path

    def generate_degradation_table(
        self,
        degradation_csv
    ):
        rows = self._read_csv(
            degradation_csv
        )

        output_path = os.path.join(
            self.output_dir,
            "ablation_degradation_table.tex"
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "\\begin{table}[htbp]\n"
            )

            file.write(
                "\\centering\n"
            )

            file.write(
                "\\caption{Absolute Metric Degradation in CRME Ablation Study}\n"
            )

            file.write(
                "\\label{tab:crme-ablation-degradation}\n"
            )

            file.write(
                "\\begin{tabular}{lccccc}\n"
            )

            file.write(
                "\\toprule\n"
            )

            file.write(
                "Configuration & MCS & SRS & KGQ & RRS & CES \\\\\n"
            )

            file.write(
                "\\midrule\n"
            )

            for row in rows:

                file.write(
                    f"{row['configuration']} & "
                    f"{self._fmt(row['mcs'])} & "
                    f"{self._fmt(row['srs'])} & "
                    f"{self._fmt(row['kgq'])} & "
                    f"{self._fmt(row['rrs'])} & "
                    f"{self._fmt(row['ces'])} \\\\\n"
                )

            file.write(
                "\\bottomrule\n"
            )

            file.write(
                "\\end{tabular}\n"
            )

            file.write(
                "\\end{table}\n"
            )

        return output_path

    def generate_all(
        self,
        metrics_csv,
        degradation_csv
    ):
        metrics_output = (
            self.generate_metrics_table(
                metrics_csv
            )
        )

        degradation_output = (
            self.generate_degradation_table(
                degradation_csv
            )
        )

        return {
            "metrics_table": metrics_output,
            "degradation_table": degradation_output
        }
