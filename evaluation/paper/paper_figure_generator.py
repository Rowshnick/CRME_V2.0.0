import csv
import os


class PaperFigureGenerator:
    """
    Generate paper-ready figure assets from canonical CRME
    evaluation evidence data.
    """

    def __init__(
        self,
        contribution_csv=(
            "evaluation/results/final/paper/"
            "figures/component_contribution.csv"
        ),
        output_dir=(
            "evaluation/results/final/paper/"
            "figures"
        ),
    ):
        self.contribution_csv = contribution_csv
        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True,
        )

    def _load_contribution_data(self):
        rows = []

        with open(
            self.contribution_csv,
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

    def generate_contribution_figure(self):
        """
        Generate a publication-ready PNG figure.
        """

        import matplotlib.pyplot as plt

        rows = self._load_contribution_data()

        rows = sorted(
            rows,
            key=lambda item: item["total_degradation"],
            reverse=True,
        )

        components = [
            row["component"].capitalize()
            for row in rows
        ]

        degradation = [
            row["total_degradation"]
            for row in rows
        ]

        fig, ax = plt.subplots(
            figsize=(8, 5)
        )

        ax.barh(
            components[::-1],
            degradation[::-1],
        )

        ax.set_xlabel(
            "Aggregate Degradation"
        )

        ax.set_ylabel(
            "CRME Component"
        )

        ax.set_title(
            "CRME Component Contribution Based on Ablation Analysis"
        )

        ax.grid(
            axis="x",
            linestyle="--",
            alpha=0.4,
        )

        output_path = os.path.join(
            self.output_dir,
            "component_contribution_ranking.png",
        )

        fig.tight_layout()

        fig.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
        )

        plt.close(fig)

        return output_path

    def generate_all(self):
        figure_path = (
            self.generate_contribution_figure()
        )

        return {
            "component_contribution_figure": figure_path,
            "status": "completed",
        }
