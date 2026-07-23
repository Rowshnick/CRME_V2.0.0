"""
CRME Evaluation Visualization Generator v1.0

Generates publication-ready figures:

1. Benchmark Comparison
2. Ablation Analysis
3. Scalability Curve

Outputs:
PNG / PDF / SVG
"""

import os
import matplotlib.pyplot as plt


OUTPUT_DIR = "evaluation/results"


def save_all_formats(fig, name):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    for fmt in [
        "png",
        "pdf",
        "svg"
    ]:

        path = os.path.join(
            OUTPUT_DIR,
            f"{name}.{fmt}"
        )

        fig.savefig(
            path,
            bbox_inches="tight",
            dpi=300
        )

        print(
            "Generated:",
            path
        )


# -------------------------------------------------
# Figure 5
# Benchmark Comparison
# -------------------------------------------------

def benchmark_comparison():

    methods = [
        "Flat File",
        "Structured Doc",
        "CRME"
    ]

    kos = [
        0,
        0.4,
        1
    ]

    dts = [
        0,
        0.5,
        1
    ]

    rsr = [
        0,
        0.6,
        1
    ]


    x = range(len(methods))


    fig, ax = plt.subplots(
        figsize=(7,4)
    )


    width = 0.25


    ax.bar(
        [i-width for i in x],
        kos,
        width,
        label="KOS"
    )

    ax.bar(
        x,
        dts,
        width,
        label="DTS"
    )

    ax.bar(
        [i+width for i in x],
        rsr,
        width,
        label="RSR"
    )


    ax.set_ylabel(
        "Score"
    )

    ax.set_title(
        "Benchmark Comparison of Research Memory Approaches"
    )


    ax.set_xticks(
        list(x)
    )

    ax.set_xticklabels(
        methods,
        rotation=15
    )


    ax.legend()


    save_all_formats(
        fig,
        "benchmark_comparison"
    )

    plt.close(fig)



# -------------------------------------------------
# Figure 6
# Ablation
# -------------------------------------------------

def ablation_analysis():

    variants = [
        "Full",
        "NoGraph",
        "NoSession",
        "NoArtifact"
    ]


    kos = [
        1,
        0,
        1,
        1
    ]

    dts = [
        1,
        1,
        1,
        1
    ]

    rsr = [
        1,
        1,
        1,
        0
    ]


    fig, ax = plt.subplots(
        figsize=(7,4)
    )


    ax.plot(
        variants,
        kos,
        marker="o",
        label="KOS"
    )

    ax.plot(
        variants,
        dts,
        marker="o",
        label="DTS"
    )

    ax.plot(
        variants,
        rsr,
        marker="o",
        label="RSR"
    )


    ax.set_ylim(
        0,
        1.1
    )


    ax.set_title(
        "CRME Ablation Analysis"
    )


    ax.set_ylabel(
        "Score"
    )


    ax.legend()


    save_all_formats(
        fig,
        "ablation_analysis"
    )


    plt.close(fig)



# -------------------------------------------------
# Figure 7
# Scalability
# -------------------------------------------------

def scalability_curve():

    datasets = [
        "Small",
        "Medium",
        "Large"
    ]


    times = [
        8.43e-06,
        1.6264e-04,
        7.9439e-04
    ]


    sizes = [
        50,
        500,
        5000
    ]


    fig, ax = plt.subplots(
        figsize=(7,4)
    )


    ax.plot(
        sizes,
        times,
        marker="o"
    )


    ax.set_xscale(
        "log"
    )

    ax.set_yscale(
        "log"
    )


    ax.set_xlabel(
        "Research Objects"
    )


    ax.set_ylabel(
        "Execution Time (seconds)"
    )


    ax.set_title(
        "CRME Scalability Evaluation"
    )


    ax.grid(
        True
    )


    save_all_formats(
        fig,
        "scalability_curve"
    )


    plt.close(fig)



def main():

    benchmark_comparison()

    ablation_analysis()

    scalability_curve()


    print(
        "\nAll evaluation figures generated successfully."
    )



if __name__ == "__main__":

    main()


