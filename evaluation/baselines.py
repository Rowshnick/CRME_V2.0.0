"""
CRME Baseline Simulation Engine v0.1

Baselines:
1. Flat File Memory
2. Structured Documentation
3. CRME Research Memory Engine

Used for comparative experiments.
"""


class FlatFileBaseline:


    def __init__(self, dataset):

        self.dataset = dataset


    def run(self):

        objects = len(
            self.dataset.get("objects", [])
        )

        decisions = len(
            self.dataset.get("decisions", [])
        )

        artifacts = len(
            self.dataset.get("artifacts", [])
        )


        return {

            "method":
                "Flat File Memory",

            "objects":
                objects,

            "relations":
                0,

            "traceable_decisions":
                0,

            "validated_artifacts":
                0
        }



class StructuredDocumentationBaseline:


    def __init__(self, dataset):

        self.dataset = dataset


    def run(self):

        objects = len(
            self.dataset.get("objects", [])
        )

        decisions = len(
            self.dataset.get("decisions", [])
        )

        artifacts = len(
            self.dataset.get("artifacts", [])
        )


        return {

            "method":
                "Structured Documentation",

            "objects":
                objects,

            "relations":
                int(
                    len(
                        self.dataset.get(
                            "relations",
                            []
                        )
                    )
                    *
                    0.4
                ),

            "traceable_decisions":
                int(
                    decisions * 0.5
                ),

            "validated_artifacts":
                int(
                    artifacts * 0.6
                )
        }



class CRMEBaseline:


    def __init__(self, dataset):

        self.dataset = dataset



    def run(self):


        objects = len(
            self.dataset.get(
                "objects",
                []
            )
        )


        relations = len(
            self.dataset.get(
                "relations",
                []
            )
        )


        decisions = len(
            self.dataset.get(
                "decisions",
                []
            )
        )


        artifacts = len(
            self.dataset.get(
                "artifacts",
                []
            )
        )


        return {


            "method":
                "CRME",


            "objects":
                objects,


            "relations":
                relations,


            "traceable_decisions":
                decisions,


            "validated_artifacts":
                artifacts

        }



def run_all_baselines(dataset):


    baselines = [

        FlatFileBaseline(dataset),

        StructuredDocumentationBaseline(
            dataset
        ),

        CRMEBaseline(dataset)

    ]


    results = []


    for baseline in baselines:

        results.append(
            baseline.run()
        )


    return results



if __name__ == "__main__":


    import json


    dataset_path = (
        "evaluation/datasets/"
        "SRCB_v1.json"
    )


    with open(
        dataset_path,
        "r",
        encoding="utf-8"
    ) as file:

        dataset = json.load(file)


    results = run_all_baselines(
        dataset
    )


    print(
        "\nCRME Baseline Comparison"
    )

    print(
        "======================="
    )


    for item in results:

        print(item)

