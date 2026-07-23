import json
import os
from datetime import datetime, timezone


class ComparisonResult:
    """
    CRME Evaluation Comparison Result

    Stores cross-dataset metric comparison results.
    """

    def __init__(
        self,
        comparison_id,
        experiment_id
    ):

        self.data = {
            "comparison_id":
                comparison_id,

            "experiment_id":
                experiment_id,

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "datasets": [],

            "metrics": {},

            "rankings": {},

            "best_dataset": {},

            "status":
                "created"
        }

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

            "comparison_id":
                self.data[
                    "comparison_id"
                ],

            "experiment_id":
                self.data[
                    "experiment_id"
                ],

            "datasets":
                len(
                    self.data[
                        "datasets"
                    ]
                ),

            "metrics":
                list(
                    self.data[
                        "metrics"
                    ].keys()
                ),

            "best_dataset":
                self.data[
                    "best_dataset"
                ],

            "status":
                self.data[
                    "status"
                ]
        }
