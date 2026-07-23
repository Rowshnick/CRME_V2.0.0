import json
import os
from datetime import datetime


class BenchmarkResult:
    """
    Standard benchmark result model for CRME Evaluation Framework

    Responsible for:
    - storing benchmark metrics
    - serialization
    - persistence
    """


    def __init__(
        self,
        benchmark_id,
        dataset_name,
        dataset_type="unknown"
    ):

        self.data = {

            "benchmark_id":
                benchmark_id,

            "dataset":
                dataset_name,

            "dataset_type":
                dataset_type,


            "runtime_sec":
                0.0,

            "memory_mb":
                0.0,

            "cpu_time":
                0.0,


            "knowledge_nodes":
                0,

            "relations":
                0,

            "sessions":
                0,

            "memories":
                0,


            "decisions":
                0,

            "goals":
                0,

            "artifacts":
                0,

            "ledger_entries":
                0,


            "ces_score":
                0.0,


            "metadata":
                {},


            "timestamp":
                datetime.utcnow()
                .isoformat()

        }



    def update(self, **kwargs):
        """
        Update benchmark metrics
        """

        for key, value in kwargs.items():

            self.data[key] = value



    def to_dict(self):

        return self.data



    def to_json(self):

        return json.dumps(
            self.data,
            indent=4
        )



    def save(self, path):

        directory = os.path.dirname(path)

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )


        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.data,
                f,
                indent=4
            )


        return path



    @classmethod
    def load(
        cls,
        path
    ):

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)


        obj = cls(
            data["benchmark_id"],
            data["dataset"],
            data.get(
                "dataset_type",
                "unknown"
            )
        )


        obj.data = data


        return obj



    def summary(self):

        return {

            "benchmark_id":
                self.data["benchmark_id"],

            "dataset":
                self.data["dataset"],

            "runtime":
                self.data["runtime_sec"],

            "memory":
                self.data["memory_mb"],

            "ces":
                self.data["ces_score"]

        }

