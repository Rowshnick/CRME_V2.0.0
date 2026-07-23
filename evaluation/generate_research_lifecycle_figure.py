from graphviz import Digraph
import os


OUTPUT_DIR = "evaluation/results"


def create_lifecycle():

    dot = Digraph(
        "Research_Memory_Lifecycle",
        engine="dot"
    )

    dot.attr(
        rankdir="TB",
        splines="ortho",
        nodesep="0.6",
        ranksep="0.8",
        bgcolor="white"
    )


    # Title

    dot.node(
        "title",
        "CRME Research Memory Lifecycle\n"
        "From Idea Generation to Knowledge Evolution",
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


    # Lifecycle nodes

    nodes = [

        (
            "idea",
            "Research Idea\n\n"
            "Initial Concept\n"
            "Research Question",
            "#D9EAF7"
        ),

        (
            "hypothesis",
            "Hypothesis\n\n"
            "Objectives\n"
            "Expected Outcomes",
            "#D9EAF7"
        ),

        (
            "planning",
            "Research Planning\n\n"
            "Tasks\n"
            "Milestones\n"
            "Dependencies",
            "#B7D7F0"
        ),

        (
            "experiment",
            "Experimentation\n\n"
            "Methods\n"
            "Evaluation\n"
            "Data",
            "#B7D7F0"
        ),

        (
            "result",
            "Research Results\n\n"
            "Findings\n"
            "Analysis",
            "#B6E3B6"
        ),

        (
            "artifact",
            "Research Artifact\n\n"
            "Code\n"
            "Dataset\n"
            "Documents",
            "#F8D7A8"
        ),

        (
            "publication",
            "Publication / Report\n\n"
            "Paper\n"
            "Technical Output",
            "#F8D7A8"
        ),

        (
            "knowledge",
            "Knowledge Update\n\n"
            "Graph Update\n"
            "Memory Consolidation",
            "#C7E8C7"
        )
    ]


    for node, label, color in nodes:

        dot.node(
            node,
            label,
            fillcolor=color
        )


    # Main lifecycle flow

    edges = [

        ("title", "idea"),

        ("idea", "hypothesis"),

        ("hypothesis", "planning"),

        ("planning", "experiment"),

        ("experiment", "result"),

        ("result", "artifact"),

        ("artifact", "publication"),

        ("publication", "knowledge"),

    ]


    for source, target in edges:

        dot.edge(
            source,
            target
        )


    # Feedback loop

    dot.edge(
        "knowledge",
        "idea",
        label="Research Feedback",
        color="blue"
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

        graph = create_lifecycle()

        graph.format = fmt

        graph.render(
            os.path.join(
                OUTPUT_DIR,
                "Research_Memory_Lifecycle"
            ),
            cleanup=True
        )


        print(
            "Generated:",
            f"Research_Memory_Lifecycle.{fmt}"
        )


if __name__ == "__main__":

    generate()


