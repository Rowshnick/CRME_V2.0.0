"""
CRME Benchmark Runner v0.1

Runs:
- Dataset loading
- Baseline execution
- Metric evaluation
- Result export

Output:
evaluation/results/
    benchmark_results.json
    comparison_table.csv
"""


import json
import csv
import os

from baselines import run_all_baselines
from metrics import CRMEMetrics



DATASET_PATH = (
    "evaluation/datasets/"
    "SRCB_v1.json"
)


RESULT_DIR = (
    "evaluation/results"
)



def load_dataset(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)



def calculate_scores(dataset, baseline):

    total_objects = len(
        dataset.get(
            "objects",
            []
        )
    )

    total_relations = len(
        dataset.get(
            "relations",
            []
        )
    )


    total_decisions = len(
        dataset.get(
            "decisions",
            []
        )
    )


    total_artifacts = len(
        dataset.get(
            "artifacts",
            []
        )
    )


    return {

        "KOS":
            round(
                baseline["relations"]
                /
                total_relations,
                3
            )
            if total_relations
            else 0,


        "DTS":
            round(
                baseline["traceable_decisions"]
                /
                total_decisions,
                3
            )
            if total_decisions
            else 0,


        "RSR":
            round(
                baseline["validated_artifacts"]
                /
                total_artifacts,
                3
            )
            if total_artifacts
            else 0
    }



def run():

    os.makedirs(
        RESULT_DIR,
        exist_ok=True
    )


    dataset = load_dataset(
        DATASET_PATH
    )


    baselines = run_all_baselines(
        dataset
    )


    results = []


    for baseline in baselines:


        scores = calculate_scores(
            dataset,
            baseline
        )


        result = {

            "method":
                baseline["method"],

            **scores

        }


        results.append(
            result
        )



    json_path = os.path.join(
        RESULT_DIR,
        "benchmark_results.json"
    )


    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )



    csv_path = os.path.join(
        RESULT_DIR,
        "comparison_table.csv"
    )


    with open(
        csv_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:


        writer = csv.DictWriter(
            file,
            fieldnames=[
                "method",
                "KOS",
                "DTS",
                "RSR"
            ]
        )


        writer.writeheader()

        writer.writerows(
            results
        )



    print(
        "\nCRME Benchmark Completed"
    )


    print(
        "======================="
    )


    for item in results:

        print(item)



    print(
        "\nGenerated:"
    )

    print(
        json_path
    )

    print(
        csv_path
    )



if __name__ == "__main__":

    run()

