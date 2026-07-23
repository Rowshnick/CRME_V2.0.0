from graphviz import Digraph
import os


OUTPUT_DIR = "evaluation/results"


def create_crme_architecture():

    dot = Digraph(
        "CRME_Architecture",
        engine="dot"
    )

    dot.attr(
        rankdir="TB",
        splines="ortho",
        nodesep="0.6",
        ranksep="0.9",
        bgcolor="white"
    )


    # Title

    dot.node(
        "title",
        "Cognitive Research Memory Engine (CRME)\n"
        "Architecture Overview",
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


    # Core layers

    dot.node(
        "researcher",
        "Researcher / AI Agent",
        fillcolor="#E8E8E8"
    )


    dot.node(
        "interaction",
        "Research Interaction Layer\n\n"
        "Queries\nIdeas\nDecisions\nUpdates",
        fillcolor="#D9EAF7"
    )


    dot.node(
        "coordinator",
        "Cognitive Coordinator\n\n"
        "Context Management\n"
        "Memory Coordination\n"
        "Knowledge Routing",
        fillcolor="#9CC3E6"
    )


    dot.node(
        "session",
        "Session Engine\n\n"
        "Temporal Memory\n"
        "Snapshots\n"
        "Continuity",
        fillcolor="#B7D7F0"
    )


    dot.node(
        "project",
        "Project Engine\n\n"
        "Lifecycle\n"
        "Milestones\n"
        "Dependencies",
        fillcolor="#B7D7F0"
    )


    dot.node(
        "graph",
        "Knowledge Graph Engine\n\n"
        "Semantic Relations\n"
        "Knowledge Links",
        fillcolor="#B7D7F0"
    )


    dot.node(
        "memory",
        "Research Memory Repository\n\n"
        "Research Objects\n"
        "Metadata\n"
        "Historical Records",
        fillcolor="#B6E3B6"
    )


    dot.node(
        "reasoning",
        "Reasoning & Intelligence Layer\n\n"
        "Analysis\nInference\nResearch Insight",
        fillcolor="#C7E8C7"
    )


    dot.node(
        "decision",
        "Decision Log",
        fillcolor="#F8D7A8"
    )


    dot.node(
        "artifact",
        "Artifact Repository",
        fillcolor="#F8D7A8"
    )


    dot.node(
        "provenance",
        "Provenance Layer",
        fillcolor="#F8D7A8"
    )


    # Main flow

    dot.edge(
        "title",
        "researcher"
    )


    dot.edge(
        "researcher",
        "interaction"
    )


    dot.edge(
        "interaction",
        "coordinator",
        label="Research Context"
    )


    dot.edge(
        "coordinator",
        "session"
    )

    dot.edge(
        "coordinator",
        "project"
    )

    dot.edge(
        "coordinator",
        "graph"
    )


    dot.edge(
        "session",
        "memory",
        label="Memory Update"
    )


    dot.edge(
        "project",
        "memory"
    )


    dot.edge(
        "graph",
        "memory"
    )


    dot.edge(
        "memory",
        "reasoning",
        label="Knowledge Retrieval"
    )


    dot.edge(
        "reasoning",
        "decision"
    )

    dot.edge(
        "reasoning",
        "artifact"
    )

    dot.edge(
        "reasoning",
        "provenance"
    )


    # Feedback loop

    dot.edge(
        "reasoning",
        "coordinator",
        label="Research Feedback",
        color="blue"
    )


    return dot



def generate():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


    for fmt in ["svg", "pdf", "png"]:

        graph = create_crme_architecture()

        graph.format = fmt

        graph.render(
            os.path.join(
                OUTPUT_DIR,
                "CRME_architecture"
            ),
            cleanup=True
        )


        print(
            "Generated:",
            f"CRME_architecture.{fmt}"
        )


if __name__ == "__main__":
    generate()

