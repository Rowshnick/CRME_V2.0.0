import os
import json
import shutil
import zipfile
from core.manifest_engine import ManifestEngine
from datetime import datetime

from core.version_engine import VersionEngine


class PackageEngine:
    """
    CRME Portable Project Package Engine v1.5.3

    Responsible for:

    - Collect CRME project state
    - Create portable package structure
    - Generate ZIP archive
    - Prepare package metadata
    - Version aware packaging
    """


    def __init__(
        self,
        base_path="."
    ):

        self.base_path = base_path

        self.version_engine = VersionEngine(
            base_path
        )


        self.storage_path = os.path.join(
            base_path,
            "storage"
        )


        self.exports_path = os.path.join(
            base_path,
            "exports"
        )


        self.package_root = os.path.join(
            self.exports_path,
            "package_build"
        )


        self.manifest_engine = ManifestEngine(
            base_path
        )


        os.makedirs(
            self.exports_path,
            exist_ok=True
        )


    # =====================================================
    # CREATE PACKAGE DIRECTORY
    # =====================================================

    def create_structure(self):

        if os.path.exists(
            self.package_root
        ):

            shutil.rmtree(
                self.package_root
            )


        folders = [
            "sessions",
            "snapshots",
            "briefs",
            "metadata"
        ]


        os.makedirs(
            self.package_root,
            exist_ok=True
        )


        for folder in folders:

            os.makedirs(
                os.path.join(
                    self.package_root,
                    folder
                ),
                exist_ok=True
            )


        return self.package_root



    # =====================================================
    # COPY CORE DATA
    # =====================================================

    def collect_storage(self):

        files = [
            "project.json",
            "graph.json"
        ]


        copied = []


        for file in files:

            source = os.path.join(
                self.storage_path,
                file
            )


            if os.path.exists(source):

                destination = os.path.join(
                    self.package_root,
                    file
                )


                shutil.copy2(
                    source,
                    destination
                )


                copied.append(file)


        return copied



    # =====================================================
    # COPY EXPORT DATA
    # =====================================================

    def collect_exports(self):

        targets = [
            "CRME_Context_Transfer.json"
        ]


        copied = []


        for file in targets:

            source = os.path.join(
                self.exports_path,
                file
            )


            if os.path.exists(source):

                destination = os.path.join(
                    self.package_root,
                    "snapshots",
                    file
                )


                shutil.copy2(
                    source,
                    destination
                )


                copied.append(file)


        return copied



    # =====================================================
    # CREATE PACKAGE METADATA
    # =====================================================

    def create_metadata(self):

        version = self.version_engine.current().get(
            "version",
            "unknown"
        )


        metadata = {

            "package_type":
                "CRME-PPP",

            "crme_version":
                version,

            "package_version":
                version,

            "created_at":
                datetime.utcnow().isoformat(),


            "contents":
            {
                "storage": True,
                "context": True,
                "graph": True
            }

        }


        path = os.path.join(
            self.package_root,
            "metadata",
            "package.json"
        )


        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:


            json.dump(
                metadata,
                f,
                indent=2,
                ensure_ascii=False
            )


        return path



    # =====================================================
    # BUILD ZIP
    # =====================================================

    def build_zip(
        self,
        name=None
    ):


        if name is None:

            version = self.version_engine.current().get(
                "version",
                "unknown"
            )


            name = (
                f"CRME-PPP-v{version}.zip"
            )


        zip_path = os.path.join(
            self.exports_path,
            name
        )


        with zipfile.ZipFile(
            zip_path,
            "w",
            zipfile.ZIP_DEFLATED
        ) as archive:


            for root, dirs, files in os.walk(
                self.package_root
            ):


                for file in files:

                    full_path = os.path.join(
                        root,
                        file
                    )


                    relative = os.path.relpath(
                        full_path,
                        self.package_root
                    )


                    archive.write(
                        full_path,
                        relative
                    )


        return zip_path




    # =====================================================
    # PUBLIC API
    # =====================================================

    def create_package(
      self,
      name=None
    ):

      self.create_structure()

      storage = self.collect_storage()

      exports = self.collect_exports()

      metadata = self.create_metadata()

      manifest = self.manifest_engine.create_manifest(
        self.package_root
      )

      zip_file = self.build_zip(
        name
      )

      return {

        "status":
            "created",

        "package":
            zip_file,

        "storage_files":
            storage,

        "export_files":
            exports,

        "metadata":
            metadata,

        "manifest":
            manifest
    }
