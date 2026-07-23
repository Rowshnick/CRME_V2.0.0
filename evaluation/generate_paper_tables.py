"""
CRME Paper Table Generator v1.1

Generates publication-ready Markdown tables
from evaluation results.
"""

import json
import os


RESULT_DIR = "evaluation/results"

OUTPUT = (
    "evaluation/results/"
    "paper_tables.md"
)



def load(name):

    path = os.path.join(
        RESULT_DIR,
        name
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



def benchmark_table(data):

    text = []

    text.append(
        "## Table 1. Benchmark Comparison\n"
    )

    text.append(
        "| Method | KOS | DTS | RSR |\n"
    )

    text.append(
        "|---|---:|---:|---:|\n"
    )

    for row in data:

        text.append(
            f"| {row['method']} | "
            f"{row['KOS']} | "
            f"{row['DTS']} | "
            f"{row['RSR']} |\n"
        )

    return "".join(text)



def ablation_table(data):

    text = []

    text.append(
        "\n## Table 2. Ablation Study\n"
    )

    text.append(
        "| Variant | CRT | KOS | DTS | RSR |\n"
    )

    text.append(
        "|---|---:|---:|---:|---:|\n"
    )


    for row in data:

        text.append(
            f"| {row['variant']} | "
            f"{row['CRT']} | "
            f"{row['KOS']} | "
            f"{row['DTS']} | "
            f"{row['RSR']} |\n"
        )

    return "".join(text)



def scalability_table(data):

    text = []

    text.append(
        "\n## Table 3. Scalability Evaluation\n"
    )

    text.append(
        "| Dataset | Objects | Sessions | Relations | Mean Time(s) | Std |\n"
    )

    text.append(
        "|---|---:|---:|---:|---:|---:|\n"
    )


    for row in data:

        text.append(
            f"| {row['dataset']} | "
            f"{row['objects']} | "
            f"{row['sessions']} | "
            f"{row['relations']} | "
            f"{row['mean_execution_time_sec']} | "
            f"{row['std_execution_time_sec']} |\n"
        )

    return "".join(text)



def main():

    benchmark = load(
        "benchmark_results.json"
    )

    ablation = load(
        "ablation_results.json"
    )

    scalability = load(
        "scalability_results.json"
    )


    content = (
        benchmark_table(benchmark)
        +
        ablation_table(ablation)
        +
        scalability_table(scalability)
    )


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(content)


    print(
        "Paper tables generated:"
    )

    print(
        OUTPUT
    )



if __name__ == "__main__":
    main()

