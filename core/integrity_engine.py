import os
import json
import hashlib
import zipfile


class IntegrityEngine:
    """
    CRME Integrity Engine v1.4

    Responsible for:

    - Verify package integrity
    - Compare SHA256 hashes
    - Validate CRME manifest
    - Detect modified files
    """



    def __init__(
        self,
        base_path="."
    ):

        self.base_path = base_path



    # =====================================================
    # SHA256
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
    # LOAD MANIFEST
    # =====================================================

    def load_manifest(
        self,
        manifest_path
    ):


        with open(
            manifest_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)



    # =====================================================
    # VERIFY DIRECTORY
    # =====================================================

    def verify_directory(
        self,
        directory,
        manifest_path
    ):


        manifest = self.load_manifest(
            manifest_path
        )


        results = []


        for item in manifest.get(
            "files",
            []
        ):


            path = os.path.join(

                directory,

                item["name"]

            )


            if not os.path.exists(
                path
            ):

                results.append(

                    {

                        "file":
                            item["name"],

                        "status":
                            "missing"

                    }

                )

                continue



            current_hash = self.sha256(
                path
            )


            results.append(

                {

                    "file":
                        item["name"],

                    "expected":
                        item["sha256"],

                    "actual":
                        current_hash,

                    "status":
                        "valid"
                        if current_hash == item["sha256"]
                        else "modified"

                }

            )


        return results



    # =====================================================
    # VERIFY ZIP PACKAGE
    # =====================================================

    def verify_zip(
        self,
        zip_path,
        manifest_path
    ):


        extract_dir = (

            zip_path
            + "_verify"

        )


        if os.path.exists(
            extract_dir
        ):

            import shutil

            shutil.rmtree(
                extract_dir
            )


        os.makedirs(
            extract_dir,
            exist_ok=True
        )


        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as archive:


            archive.extractall(
                extract_dir
            )



        results = self.verify_directory(

            extract_dir,

            manifest_path

        )


        valid = all(

            r["status"] == "valid"

            for r in results

        )


        return {


            "package":
                zip_path,


            "checked_files":
                len(results),


            "integrity":
                "PASSED"
                if valid
                else "FAILED",


            "details":
                results

        }

