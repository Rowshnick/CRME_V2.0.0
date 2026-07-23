import os
import json
from datetime import datetime


class DatasetRegistry:
    """
    CRME Dataset Registry

    Responsible for:
    - Dataset registration
    - Dataset discovery
    - Metadata storage
    - Dataset lifecycle management
    """

    def __init__(self, base_path="."):

        self.registry_dir = os.path.join(
            base_path,
            "evaluation",
            "datasets"
        )

        os.makedirs(
            self.registry_dir,
            exist_ok=True
        )

        self.registry_file = os.path.join(
            self.registry_dir,
            "registry.json"
        )

        self.datasets = self.load()


    # -------------------------------------------------
    # LOAD REGISTRY
    # -------------------------------------------------

    def load(self):

        if not os.path.exists(
            self.registry_file
        ):
            return {}

        with open(
            self.registry_file,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)


    # -------------------------------------------------
    # SAVE REGISTRY
    # -------------------------------------------------

    def save(self):

        with open(
            self.registry_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.datasets,
                f,
                indent=4,
                ensure_ascii=False
            )


    # -------------------------------------------------
    # REGISTER DATASET
    # -------------------------------------------------

    def register(
        self,
        name,
        version,
        source,
        path,
        description="",
        metadata=None
    ):

        dataset_id = (
            f"{name}_{version}"
            .replace(" ", "_")
        )


        record = {

            "dataset_id": dataset_id,

            "name": name,

            "version": version,

            "source": source,

            "path": path,

            "description": description,

            "metadata": metadata or {},

            "created_at":
                datetime.utcnow()
                .isoformat()

        }


        self.datasets[dataset_id] = record

        self.save()


        return record



    # -------------------------------------------------
    # GET DATASET
    # -------------------------------------------------

    def get(
        self,
        dataset_id
    ):

        return self.datasets.get(
            dataset_id
        )


    # -------------------------------------------------
    # LIST DATASETS
    # -------------------------------------------------

    def list(self):

        return list(
            self.datasets.values()
        )


    # -------------------------------------------------
    # REMOVE DATASET
    # -------------------------------------------------

    def remove(
        self,
        dataset_id
    ):

        if dataset_id in self.datasets:

            del self.datasets[dataset_id]

            self.save()

            return True


        return False



    # -------------------------------------------------
    # SUMMARY
    # -------------------------------------------------

    def summary(self):

        return {

            "datasets":
                len(self.datasets),

            "sources":
                list(
                    set(
                        d["source"]
                        for d in self.datasets.values()
                    )
                )

        }

