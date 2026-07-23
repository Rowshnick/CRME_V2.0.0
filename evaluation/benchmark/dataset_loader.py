import os
import json
import csv


class DatasetLoader:
    """
    Unified Dataset Loader for CRME Evaluation Framework.

    Supports:
    - JSON datasets
    - CSV datasets
    - Structured Research Benchmark datasets (SRCB)
    """

    def load(self, dataset):
        path = dataset.get("path")

        if not path:
            raise ValueError("Dataset path is missing")

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Dataset file not found: {path}"
            )

        extension = os.path.splitext(path)[1].lower()

        if extension == ".json":
            return self._load_json(dataset)

        if extension == ".csv":
            return self._load_csv(dataset)

        raise ValueError(
            f"Unsupported dataset format: {extension}"
        )

    # =====================================================
    # JSON LOADER
    # =====================================================

    def _load_json(self, dataset):
        path = dataset["path"]

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = {
            "name": dataset.get("name"),
            "format": "json",
            "dataset_type": "generic",
            "sample_count": 0,
            "object_count": 0,
            "relation_count": 0,
            "session_count": 0,
            "decision_count": 0,
            "artifact_count": 0,
            "total_records": 0,
            "data": data
        }

        # ---------------------------------------------
        # SRCB / Structured Research Benchmark
        # ---------------------------------------------

        structured_keys = {
            "objects",
            "relations",
            "sessions",
            "decisions",
            "artifacts"
        }

        if isinstance(data, dict) and structured_keys.intersection(
            data.keys()
        ):

            result["dataset_type"] = (
                "structured_research_benchmark"
            )

            result["object_count"] = len(
                data.get("objects", [])
            )

            result["relation_count"] = len(
                data.get("relations", [])
            )

            result["session_count"] = len(
                data.get("sessions", [])
            )

            result["decision_count"] = len(
                data.get("decisions", [])
            )

            result["artifact_count"] = len(
                data.get("artifacts", [])
            )

            result["sample_count"] = (
                result["object_count"]
            )

            result["total_records"] = (
                result["object_count"]
                + result["relation_count"]
                + result["session_count"]
                + result["decision_count"]
                + result["artifact_count"]
            )

            return result

        # ---------------------------------------------
        # Generic JSON List
        # ---------------------------------------------

        if isinstance(data, list):

            result["dataset_type"] = "generic_json"

            result["sample_count"] = len(data)
            result["total_records"] = len(data)

            return result

        # ---------------------------------------------
        # Generic JSON with samples
        # ---------------------------------------------

        if isinstance(data, dict):

            samples = data.get("samples", [])

            if isinstance(samples, list):

                result["dataset_type"] = (
                    "structured_samples"
                )

                result["sample_count"] = len(samples)
                result["total_records"] = len(samples)

        return result

    # =====================================================
    # CSV LOADER
    # =====================================================

    def _load_csv(self, dataset):

        path = dataset["path"]

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            reader = csv.DictReader(f)

            rows = list(reader)

        return {
            "name": dataset.get("name"),
            "format": "csv",
            "dataset_type": "tabular",
            "sample_count": len(rows),
            "object_count": 0,
            "relation_count": 0,
            "session_count": 0,
            "decision_count": 0,
            "artifact_count": 0,
            "total_records": len(rows),
            "columns": reader.fieldnames or [],
            "data": rows
        }

