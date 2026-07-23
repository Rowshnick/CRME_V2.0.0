import os
import json
import hashlib
from datetime import datetime
import uuid


class ManifestEngine:
    """
    CRME Manifest Engine v1.4

    Responsible for:

    - Generate package manifest
    - Track package metadata
    - Inventory files
    - Calculate SHA256 hashes
    - Record CRME state metrics

    Output:
        CRME_MANIFEST.json
    """



    def __init__(
        self,
        base_path="."
    ):

        self.base_path = base_path

        self.exports_path = os.path.join(
            base_path,
            "exports"
        )

        os.makedirs(
            self.exports_path,
            exist_ok=True
        )



    # =====================================================
    # FILE HASH
    # =====================================================

    def sha256(
        self,
        file_path
    ):

        h = hashlib.sha256()


        with open(
            file_path,
            "rb"
        ) as f:

            for chunk in iter(
                lambda: f.read(4096),
                b""
            ):

                h.update(
                    chunk
                )


        return h.hexdigest()



    # =====================================================
    # INVENTORY
    # =====================================================

    def scan_files(
        self,
        directory
    ):

        files = []


        for root, dirs, filenames in os.walk(
            directory
        ):

            for filename in filenames:

                path = os.path.join(
                    root,
                    filename
                )


                relative = os.path.relpath(
                    path,
                    directory
                )


                files.append(

                    {

                        "name":
                            relative,

                        "size":
                            os.path.getsize(
                                path
                            ),

                        "sha256":
                            self.sha256(
                                path
                            )

                    }

                )


        return files



    # =====================================================
    # CRME METRICS
    # =====================================================

    def collect_metrics(
        self
    ):

        metrics = {

            "nodes": 0,

            "relations": 0,

            "sessions": 0,

            "decisions": 0,

            "goals": 0

        }


        graph_path = os.path.join(
            self.base_path,
            "storage",
            "graph.json"
        )


        project_path = os.path.join(
            self.base_path,
            "storage",
            "project.json"
        )


        if os.path.exists(
            graph_path
        ):

            with open(
                graph_path,
                "r",
                encoding="utf-8"
            ) as f:

                graph = json.load(f)


            metrics["nodes"] = len(
                graph.get(
                    "objects",
                    []
                )
            )


            metrics["relations"] = len(
                graph.get(
                    "relations",
                    []
                )
            )


        if os.path.exists(
            project_path
        ):

            with open(
                project_path,
                "r",
                encoding="utf-8"
            ) as f:

                project = json.load(f)


            metrics["sessions"] = len(
                project.get(
                    "sessions",
                    []
                )
            )


            metrics["decisions"] = len(
                project.get(
                    "decision_log",
                    []
                )
            )


            metrics["goals"] = len(
                project.get(
                    "idea_inbox",
                    []
                )
            )


        return metrics



    # =====================================================
    # BUILD MANIFEST
    # =====================================================

    def create_manifest(
        self,
        package_path
    ):

        manifest = {


            "manifest_version":
                "1.0",


            "package_format":
                "CRME-PPP",


            "package_id":
                "CRME-PKG-" + str(
                    uuid.uuid4()
                )[:8],


            "created_at":
                datetime.utcnow().isoformat(),


            "files":
                self.scan_files(
                    package_path
                ),


            "crme_metrics":
                self.collect_metrics()


        }


        output = os.path.join(
            self.exports_path,
            "CRME_MANIFEST.json"
        )


        with open(
            output,
            "w",
            encoding="utf-8"
        ) as f:


            json.dump(
                manifest,
                f,
                indent=2,
                ensure_ascii=False
            )


        return output

