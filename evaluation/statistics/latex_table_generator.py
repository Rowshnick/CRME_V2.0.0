import json
import os


class StatisticalLatexTableGenerator:
    """
    Generate paper-ready LaTeX tables from CRME statistical analysis JSON.
    """

    def __init__(
        self,
        output_dir="evaluation/results/statistics/latex"
    ):
        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    # =====================================================
    # LOAD
    # =====================================================

    def _load_json(
        self,
        path
    ):
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    # =====================================================
    # FORMAT
    # =====================================================

    def _fmt(
        self,
        value
    ):
        try:
            return f"{float(value):.2f}"

        except (
            TypeError,
            ValueError
        ):
            return str(value)

    # =====================================================
    # NORMALIZE COMPONENT ANALYSIS
    # =====================================================

    def _get_components(
        self,
        analysis
    ):
        return analysis.get(
            "component_analysis",
            {}
        )

    # =====================================================
    # COMPONENT RANKING
    # =====================================================

    def generate_component_ranking(
        self,
        analysis
    ):
        output_path = os.path.join(
            self.output_dir,
            "component_ranking.tex"
        )

        components = self._get_components(
            analysis
        )

        ranking = []

        for component, data in components.items():

            ranking.append(
                {
                    "component": component,
                    "degradation": data.get(
                        "total_degradation",
                        0
                    ),
                    "rank": data.get(
                        "contribution_rank",
                        999
                    )
                }
            )

        ranking.sort(
            key=lambda item: item["rank"]
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
                "\\caption{Component Contribution Ranking "
                "Based on Ablation Analysis}\n"
            )

            file.write(
                "\\label{tab:crme-component-ranking}\n"
            )

            file.write(
                "\\begin{tabular}{lcc}\n"
            )

            file.write(
                "\\toprule\n"
            )

            file.write(
                "Rank & Component & Aggregate Degradation "
                "\\\\\n"
            )

            file.write(
                "\\midrule\n"
            )

            for index, item in enumerate(
                ranking,
                start=1
            ):

                component = item[
                    "component"
                ].capitalize()

                degradation = item[
                    "degradation"
                ]

                file.write(
                    f"{index} & "
                    f"{component} & "
                    f"{self._fmt(degradation)} "
                    "\\\\\n"
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

    # =====================================================
    # DETAILED COMPONENT STATISTICS
    # =====================================================

    def generate_component_statistics(
        self,
        analysis
    ):
        output_path = os.path.join(
            self.output_dir,
            "component_statistics.tex"
        )

        components = self._get_components(
            analysis
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
                "\\caption{Detailed Component-Level "
                "Ablation Statistics}\n"
            )

            file.write(
                "\\label{tab:crme-component-statistics}\n"
            )

            file.write(
                "\\begin{tabular}{llrrr}\n"
            )

            file.write(
                "\\toprule\n"
            )

            file.write(
                "Component & Metric & Baseline & "
                "Ablated & Degradation \\\\\n"
            )

            file.write(
                "\\midrule\n"
            )

            for component, data in components.items():

                metrics = data.get(
                    "metrics",
                    {}
                )

                first_metric = True

                for metric, values in metrics.items():

                    component_label = (
                        component.capitalize()
                        if first_metric
                        else ""
                    )

                    baseline = values.get(
                        "baseline",
                        0
                    )

                    ablated = values.get(
                        "ablated",
                        0
                    )

                    degradation = values.get(
                        "absolute_degradation",
                        0
                    )

                    file.write(
                        f"{component_label} & "
                        f"{metric.upper()} & "
                        f"{self._fmt(baseline)} & "
                        f"{self._fmt(ablated)} & "
                        f"{self._fmt(degradation)} "
                        "\\\\\\n"
                    )

                    first_metric = False

                file.write(
                    "\\midrule\n"
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

    # =====================================================
    # STATISTICAL SUMMARY
    # =====================================================

    def generate_summary_table(
        self,
        analysis
    ):
        output_path = os.path.join(
            self.output_dir,
            "statistical_summary.tex"
        )

        baseline = (
            analysis
            .get(
                "metrics",
                {}
            )
            .get(
                "baseline",
                {}
            )
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
                "\\caption{CRME Statistical Evaluation Summary}\n"
            )

            file.write(
                "\\label{tab:crme-statistical-summary}\n"
            )

            file.write(
                "\\begin{tabular}{lc}\n"
            )

            file.write(
                "\\toprule\n"
            )

            file.write(
                "Metric & Baseline Score \\\\\n"
            )

            file.write(
                "\\midrule\n"
            )

            for metric, value in baseline.items():

                file.write(
                    f"{metric.upper()} & "
                    f"{self._fmt(value)} "
                    "\\\\\n"
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

    # =====================================================
    # GENERATE ALL
    # =====================================================

    def generate_all(
        self,
        analysis_json
    ):
        analysis = self._load_json(
            analysis_json
        )

        return {
            "ranking": self.generate_component_ranking(
                analysis
            ),

            "component_statistics": (
                self.generate_component_statistics(
                    analysis
                )
            ),

            "summary": self.generate_summary_table(
                analysis
            )
        }

