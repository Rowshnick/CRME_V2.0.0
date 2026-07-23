import json
import os
from datetime import datetime, timezone


class ExperimentResult:
    """
    CRME Evaluation Experiment Result

    Stores the results of evaluating one or more datasets
    in a single reproducible experiment.
    """

    def __init__(
        self,
        experiment_id,
        datasets=None
    ):
        self.data = {
            "experiment_id": experiment_id,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "status": "created",

            "datasets": datasets or [],

            "runs": 0,

            "results": [],

            "summary": {}
        }

    # =====================================================
    # ADD RESULT
    # =====================================================

    def add_result(
        self,
        result
    ):
        self.data["results"].append(
            result
        )

        self.data["runs"] = len(
            self.data["results"]
        )

    # =====================================================
    # UPDATE STATUS
    # =====================================================

    def set_status(
        self,
        status
    ):
        self.data["status"] = status

    # =====================================================
    # SET SUMMARY
    # =====================================================

    def set_summary(
        self,
        summary
    ):
        self.data["summary"] = summary

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(
        self
    ):
        return self.data

    def to_json(
        self
    ):
        return json.dumps(
            self.data,
            indent=4
        )

    # =====================================================
    # SAVE
    # =====================================================

    def save(
        self,
        path
    ):
        directory = os.path.dirname(
            path
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.data,
                file,
                indent=4
            )

        return path

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self
    ):
        return {
            "experiment_id":
                self.data["experiment_id"],

            "datasets":
                len(
                    self.data["datasets"]
                ),

            "runs":
                self.data["runs"],

            "status":
                self.data["status"],

            "metrics":
                self.data["summary"]
        }
