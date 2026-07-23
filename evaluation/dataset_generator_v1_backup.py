"""
CRME Synthetic Research Continuity Benchmark (SRCB)

Dataset Generator v0.1

Generates reproducible synthetic research workflows
for CRME evaluation experiments.
"""

import json
import random
import os
from datetime import datetime, timezone

class SyntheticResearchDataset:

    def __init__(
        self,
        seed=42,
        objects_count=50,
        sessions_count=10,
        decisions_count=20,
        artifacts_count=15
    ):

        random.seed(seed)

        self.seed = seed
        self.objects_count = objects_count
        self.sessions_count = sessions_count
        self.decisions_count = decisions_count
        self.artifacts_count = artifacts_count

        self.dataset = {
            "dataset": "SRCB-v1",
            "project": "Smart Transportation AI Research",
            "created": datetime.now(timezone.utc).isoformat() ,

            "objects": [],
            "relations": [],
            "sessions": [],
            "decisions": [],
            "artifacts": []
        }


    def generate_objects(self):

        object_types = [
            "research_goal",
            "paper",
            "method",
            "experiment",
            "result",
            "idea"
        ]

        for i in range(1, self.objects_count + 1):

            obj = {
                "id": f"OBJ-{i:03}",
                "type": random.choice(object_types),
                "title": f"Research Entity {i}",
                "timestamp":
                    datetime.now(timezone.utc).isoformat()
            }

            self.dataset["objects"].append(obj)


    def generate_relations(self):

        relation_types = [
            "supports",
            "requires",
            "produces",
            "depends_on",
            "extends"
        ]

        for i in range(self.objects_count * 2):

            source = random.randint(
                1,
                self.objects_count
            )

            target = random.randint(
                1,
                self.objects_count
            )

            if source != target:

                relation = {
                    "source":
                        f"OBJ-{source:03}",

                    "target":
                        f"OBJ-{target:03}",

                    "type":
                        random.choice(relation_types)
                }

                self.dataset["relations"].append(
                    relation
                )


    def generate_sessions(self):

        activities = [
            "Problem Definition",
            "Literature Review",
            "Method Selection",
            "Experiment Design",
            "Simulation",
            "Evaluation",
            "Revision"
        ]

        for i in range(1, self.sessions_count + 1):

            session = {

                "id":
                    f"S-{i:02}",

                "activity":
                    random.choice(activities),

                "status":
                    "completed",

                "timestamp":
                    datetime.now(timezone.utc).isoformat()
            }

            self.dataset["sessions"].append(
                session
            )


    def generate_decisions(self):

        for i in range(1, self.decisions_count + 1):

            decision = {

                "id":
                    f"DEC-{i:03}",

                "decision":
                    f"Research decision {i}",

                "reason":
                    "Based on previous research evidence",

                "linked_object":
                    f"OBJ-{random.randint(1,self.objects_count):03}"

            }

            self.dataset["decisions"].append(
                decision
            )


    def generate_artifacts(self):

        artifact_types = [
            "paper",
            "code",
            "experiment_log",
            "report"
        ]

        for i in range(1, self.artifacts_count + 1):

            artifact = {

                "id":
                    f"ART-{i:03}",

                "type":
                    random.choice(artifact_types),

                "version":
                    "v1.0",

                "source":
                    "SRCB-v1"

            }

            self.dataset["artifacts"].append(
                artifact
            )


    def build(self):

        self.generate_objects()
        self.generate_relations()
        self.generate_sessions()
        self.generate_decisions()
        self.generate_artifacts()

        return self.dataset



def save_dataset(path):

    generator = SyntheticResearchDataset()

    dataset = generator.build()

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            dataset,
            f,
            indent=4,
            ensure_ascii=False
        )


    return dataset



if __name__ == "__main__":

    output = (
        "evaluation/datasets/"
        "SRCB_v1.json"
    )

    data = save_dataset(output)

    print(
        "SRCB Dataset Generated"
    )

    print(
        {
            "objects":
                len(data["objects"]),

            "relations":
                len(data["relations"]),

            "sessions":
                len(data["sessions"]),

            "decisions":
                len(data["decisions"]),

            "artifacts":
                len(data["artifacts"])
        }
    )

