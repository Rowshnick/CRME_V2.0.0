"""
SRCB Dataset Generator v1.1

Synthetic Research Continuity Benchmark

Generates a reproducible research memory benchmark containing:

- Research Objects
- Semantic Relations
- Research Sessions
- Decisions
- Research Artifacts
"""

import json
import os
import random
from datetime import datetime, timezone


OUTPUT = "evaluation/datasets/SRCB_v1.json"


OBJECT_TYPES = [
    "paper",
    "experiment",
    "dataset",
    "decision",
    "idea",
    "code_artifact"
]


RELATION_TYPES = [
    "supports",
    "derived_from",
    "validates",
    "depends_on",
    "references"
]


SESSION_TYPES = [
    "research_session",
    "review_session",
    "experiment_session"
]


ARTIFACT_TYPES = [
    "code",
    "dataset",
    "report",
    "figure"
]


def generate_dataset(
        objects_count=50,
        sessions_count=10
):

    random.seed(42)


    objects = []

    for i in range(objects_count):

        objects.append(
            {
                "id": f"O{i}",
                "type": random.choice(
                    OBJECT_TYPES
                ),
                "created":
                    datetime.now(
                        timezone.utc
                    ).isoformat()
            }
        )


    # -----------------------------
    # Semantic Relations
    # -----------------------------

    relations = []

    for i in range(objects_count):

        for j in range(2):

            target = (
                i + j + 1
            ) % objects_count


            relations.append(
                {
                    "source":
                        f"O{i}",

                    "target":
                        f"O{target}",

                    "relation":
                        random.choice(
                            RELATION_TYPES
                        )
                }
            )


    # -----------------------------
    # Research Sessions
    # -----------------------------

    sessions = []

    for i in range(sessions_count):

        sessions.append(
            {
                "id":
                    f"S{i}",

                "type":
                    random.choice(
                        SESSION_TYPES
                    ),

                "status":
                    "completed"
            }
        )


    # -----------------------------
    # Decisions
    # -----------------------------

    decisions = []

    for i in range(
        sessions_count * 2
    ):

        decisions.append(
            {
                "id":
                    f"D{i}",

                "session":
                    f"S{i % sessions_count}",

                "linked_object":
                    f"O{i % objects_count}"
            }
        )


    # -----------------------------
    # Artifacts
    # -----------------------------

    artifacts = []

    for i in range(15):

        artifacts.append(
            {
                "id":
                    f"A{i}",

                "type":
                    random.choice(
                        ARTIFACT_TYPES
                    ),

                "version":
                    "1.0",

                "validated":
                    True
            }
        )


    return {

        "benchmark":
            "SRCB_v1.1",

        "created":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "objects":
            objects,

        "relations":
            relations,

        "sessions":
            sessions,

        "decisions":
            decisions,

        "artifacts":
            artifacts

    }



def main():

    os.makedirs(
        "evaluation/datasets",
        exist_ok=True
    )


    dataset = generate_dataset()


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            dataset,
            file,
            indent=4
        )


    print(
        "SRCB Dataset v1.1 Generated"
    )


    print(
        {
            "objects":
                len(dataset["objects"]),

            "relations":
                len(dataset["relations"]),

            "sessions":
                len(dataset["sessions"]),

            "decisions":
                len(dataset["decisions"]),

            "artifacts":
                len(dataset["artifacts"])
        }
    )



if __name__ == "__main__":

    main()

