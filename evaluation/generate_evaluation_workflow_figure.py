from graphviz import Digraph
import os


OUTPUT_DIR = "evaluation/results"


def create_workflow():

    dot = Digraph(
        "CRME_Evaluation_Workflow",
        engine="dot"
    )


    dot.attr(
        rankdir="TB",
        splines="ortho",
        bgcolor="white",
        nodesep="0.6",
        ranksep="0.8"
    )


    dot.node(
        "title",
        "CRME Evaluation Workflow\n"
        "Experimental Validation Framework",
        shape="plaintext",
        fontname="Helvetica-Bold",
        fontsize="16"
    )


    dot.attr(
        "node",
        shape="box",
        style="rounded,filled",
        fontname="Helvetica",
        fontsize="12"
    )


    dot.node(
        "implementation",
        "CRME Implementation\n\n"
        "Core Modules\n"
        "Memory\n"
        "Session\n"
        "Project\n"
        "Graph",
        fillcolor="#9CC3E6"
    )


    dot.node(
        "framework",
        "Evaluation Framework\n\n"
        "Experimental Pipeline",
        fillcolor="#D9EAF7"
    )


    dot.node(
        "benchmark",
        "Benchmark Evaluation\n\n"
        "Baseline Comparison\n"
        "KOS / DTS / RSR",
        fillcolor="#B7D7F0"
    )


    dot.node(
        "ablation",
        "Ablation Study\n\n"
        "Component Contribution\n"
        "CRME Variants",
        fillcolor="#B7D7F0"
    )


    dot.node(
        "scalability",
        "Scalability Evaluation\n\n"
        "Small\nMedium\nLarge",
        fillcolor="#B7D7F0"
    )


    dot.node(
        "metrics",
        "Metric Computation\n\n"
        "CRT\nKOS\nDTS\nRSR",
        fillcolor="#B6E3B6"
    )


    dot.node(
        "tables",
        "Paper Tables & Analysis\n\n"
        "Quantitative Results\n"
        "Discussion",
        fillcolor="#F8D7A8"
    )


    dot.edge(
        "title",
        "implementation"
    )


    dot.edge(
        "implementation",
        "framework"
    )


    dot.edge(
        "framework",
        "benchmark"
    )

    dot.edge(
        "framework",
        "ablation"
    )

    dot.edge(
        "framework",
        "scalability"
    )


    dot.edge(
        "benchmark",
        "metrics"
    )

    dot.edge(
        "ablation",
        "metrics"
    )

    dot.edge(
        "scalability",
        "metrics"
    )


    dot.edge(
        "metrics",
        "tables"
    )


    return dot



def generate():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


    for fmt in [
        "svg",
        "pdf",
        "png"
    ]:

        graph = create_workflow()

        graph.format = fmt

        graph.render(
            os.path.join(
                OUTPUT_DIR,
                "CRME_Evaluation_Workflow"
            ),
            cleanup=True
        )


        print(
            "Generated:",
            f"CRME_Evaluation_Workflow.{fmt}"
        )


if __name__ == "__main__":
    generate()

