"""
CRME Evaluation Metrics Engine v0.1

Metrics:
1. Context Recovery Time (CRT)
2. Knowledge Organization Score (KOS)
3. Decision Traceability Score (DTS)
4. Reproducibility Success Rate (RSR)

Designed for SRCB benchmark evaluation.
"""

import json
import os


class CRMEMetrics:


    def __init__(self, dataset):

        self.dataset = dataset


    # -----------------------------------------
    # Context Recovery Time
    # -----------------------------------------

    def context_recovery_time(self):

        sessions = len(
            self.dataset.get("sessions", [])
        )

        objects = len(
            self.dataset.get("objects", [])
        )

        if sessions == 0:
            return 0

        # Simulated normalized recovery cost
        score = objects / sessions

        return round(score, 3)



    # -----------------------------------------
    # Knowledge Organization Score
    # -----------------------------------------

    def knowledge_organization_score(self):

        objects = len(
            self.dataset.get("objects", [])
        )

        relations = len(
            self.dataset.get("relations", [])
        )


        if objects == 0:
            return 0


        relation_density = (
            relations / objects
        )


        # normalize to [0,1]

        score = min(
            relation_density / 2,
            1
        )


        return round(score, 3)



    # -----------------------------------------
    # Decision Traceability Score
    # -----------------------------------------

    def decision_traceability_score(self):

        decisions = self.dataset.get(
            "decisions",
            []
        )


        if len(decisions) == 0:
            return 0


        linked = 0


        for decision in decisions:

            if decision.get(
                "linked_object"
            ):

                linked += 1


        score = (
            linked /
            len(decisions)
        )


        return round(score, 3)



    # -----------------------------------------
    # Reproducibility Success Rate
    # -----------------------------------------

    def reproducibility_success_rate(self):

        artifacts = self.dataset.get(
            "artifacts",
            []
        )


        if len(artifacts) == 0:
            return 0


        valid = 0


        for artifact in artifacts:

            required = [
                "id",
                "type",
                "version",
                "source"
            ]


            if all(
                key in artifact
                for key in required
            ):
                valid += 1


        score = (
            valid /
            len(artifacts)
        )


        return round(score, 3)



    # -----------------------------------------
    # Complete Evaluation
    # -----------------------------------------

    def evaluate(self):

        return {

            "CRT":
                self.context_recovery_time(),

            "KOS":
                self.knowledge_organization_score(),

            "DTS":
                self.decision_traceability_score(),

            "RSR":
                self.reproducibility_success_rate()

        }



def load_dataset(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)



if __name__ == "__main__":


    dataset_path = (
        "evaluation/datasets/"
        "SRCB_v1.json"
    )


    if not os.path.exists(dataset_path):

        print(
            "Dataset not found."
        )

        exit(1)



    dataset = load_dataset(
        dataset_path
    )


    evaluator = CRMEMetrics(
        dataset
    )


    results = evaluator.evaluate()


    print(
        "\nCRME Evaluation Metrics"
    )

    print(
        "======================"
    )

    print(
        results
    )

