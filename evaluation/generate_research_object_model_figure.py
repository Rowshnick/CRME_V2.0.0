from graphviz import Digraph
import os


OUTPUT_DIR = "evaluation/results"


def create_object_model():

    dot = Digraph(
        "Research_Object_Model",
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
        "CRME Research Object Model\n"
        "Structured Representation of Research Knowledge",
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
        "object",
        "Research Object\n\n"
        "Core Knowledge Unit",
        fillcolor="#9CC3E6"
    )


    dot.node(
        "identity",
        "Identity\n\n"
        "Object ID\n"
        "Type",
        fillcolor="#D9EAF7"
    )


    dot.node(
        "metadata",
        "Metadata\n\n"
        "Properties\n"
        "Tags\n"
        "Attributes",
        fillcolor="#D9EAF7"
    )


    dot.node(
        "temporal",
        "Temporal Context\n\n"
        "Creation Time\n"
        "History\n"
        "Versions",
        fillcolor="#D9EAF7"
    )


    dot.node(
        "relations",
        "Semantic Relations\n\n"
        "Links\n"
        "Dependencies\n"
        "Knowledge Graph",
        fillcolor="#B6E3B6"
    )


    dot.node(
        "provenance",
        "Provenance\n\n"
        "Source\n"
        "Decisions\n"
        "Evolution",
        fillcolor="#F8D7A8"
    )


    dot.node(
        "artifact",
        "Research Artifacts\n\n"
        "Code\n"
        "Dataset\n"
        "Documents\n"
        "Results",
        fillcolor="#F8D7A8"
    )


    dot.edge("title", "object")


    for target in [
        "identity",
        "metadata",
        "temporal",
        "relations",
        "provenance",
        "artifact"
    ]:
        dot.edge(
            "object",
            target
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

        graph = create_object_model()

        graph.format = fmt

        graph.render(
            os.path.join(
                OUTPUT_DIR,
                "Research_Object_Model"
            ),
            cleanup=True
        )


        print(
            "Generated:",
            f"Research_Object_Model.{fmt}"
        )


if __name__ == "__main__":
    generate()

