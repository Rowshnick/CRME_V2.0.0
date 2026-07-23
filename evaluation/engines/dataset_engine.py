from evaluation.engines.dataset_registry import DatasetRegistry

from evaluation.importers.csv_importer import CSVImporter
from evaluation.importers.json_importer import JSONImporter
from evaluation.importers.public_dataset_loader import PublicDatasetLoader
import os

from evaluation.engines.dataset_registry import DatasetRegistry


class DatasetEngine:
    """
    CRME Dataset Engine

    Central manager for evaluation datasets.

    Supported sources:
    - synthetic
    - public
    - manual
    """


    def __init__(self, base_path="."):

        self.base_path = base_path

        self.registry = DatasetRegistry(
            base_path
        )

        self.csv_importer = CSVImporter()

        self.json_importer = JSONImporter()

        self.public_loader = PublicDatasetLoader()

    # -------------------------------------------------
    # REGISTER DATASET
    # -------------------------------------------------

    def add_dataset(
        self,
        name,
        version,
        source,
        path,
        description="",
        metadata=None
    ):

        return self.registry.register(
            name=name,
            version=version,
            source=source,
            path=path,
            description=description,
            metadata=metadata
        )


    # -------------------------------------------------
    # SYNTHETIC DATASET
    # -------------------------------------------------

    def add_synthetic(
        self,
        name,
        version,
        path,
        metadata=None
    ):

        return self.add_dataset(
            name=name,
            version=version,
            source="synthetic",
            path=path,
            description=
            "Synthetic evaluation dataset",
            metadata=metadata
        )


    # -------------------------------------------------
    # PUBLIC DATASET
    # -------------------------------------------------

    def add_public(
        self,
        name,
        version,
        path,
        provider,
        metadata=None
    ):

        meta = metadata or {}

        meta["provider"] = provider


        return self.add_dataset(
            name=name,
            version=version,
            source="public",
            path=path,
            description=
            "External public dataset",
            metadata=meta
        )


    # -------------------------------------------------
    # MANUAL IMPORT
    # -------------------------------------------------

    def add_manual(
        self,
        name,
        version,
        path,
        metadata=None
    ):

        return self.add_dataset(
            name=name,
            version=version,
            source="manual",
            path=path,
            description=
            "Manually imported dataset",
            metadata=metadata
        )


    # -------------------------------------------------
    # QUERY
    # -------------------------------------------------

    def list(self):

        return self.registry.list()


    def get(
        self,
        dataset_id
    ):

        return self.registry.get(
            dataset_id
        )


    # -------------------------------------------------
    # IMPORT CSV DATASET
    # -------------------------------------------------

    def import_csv(
        self,
        name,
        version,
        path,
        description="CSV imported dataset"
    ):

        schema = self.csv_importer.schema(path)


        return self.add_dataset(

            name=name,

            version=version,

            source="manual",

            path=path,

            description=description,

            metadata={
                "format": "csv",
                "schema": schema
            }
        )

    # -------------------------------------------------
    # IMPORT JSON DATASET
    # -------------------------------------------------

    def import_json(
        self,
        name,
        version,
        path,
        description="JSON imported dataset"
    ):

        schema = self.json_importer.schema(path)


        return self.add_dataset(

            name=name,

            version=version,

            source="manual",

            path=path,

            description=description,

            metadata={
                "format": "json",
                "schema": schema
            }
        )
    # -------------------------------------------------
    # REGISTER PUBLIC DATASET
    # -------------------------------------------------

    def import_public(
        self,
        name,
        version,
        path,
        provider,
        url
    ):


        metadata = self.public_loader.create_metadata(

            name=name,

            provider=provider,

            url=url

        )


        return self.add_dataset(

            name=name,

            version=version,

            source="public",

            path=path,

            description=
            "External public dataset",

            metadata=metadata

        )



    def summary(self):

        return self.registry.summary()

