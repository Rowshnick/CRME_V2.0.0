import os
import json
from datetime import datetime


class VersionEngine:
    """
    CRME Version Engine v1.4

    Responsible for:

    - Track CRME evolution
    - Store release history
    - Manage version metadata
    - Prepare future migrations
    """



    def __init__(
        self,
        base_path="."
    ):

        self.base_path = base_path

        self.storage_path = os.path.join(
            base_path,
            "storage"
        )

        os.makedirs(
            self.storage_path,
            exist_ok=True
        )


        self.version_file = os.path.join(
            self.storage_path,
            "crme_versions.json"
        )


        self._initialize()



    # =====================================================
    # INITIALIZE
    # =====================================================

    def _initialize(self):

        if not os.path.exists(
            self.version_file
        ):

            data = {

                "system":
                    "CRME",

                "current_version":
                    "1.4",

                "created_at":
                    datetime.utcnow().isoformat(),

                "history":
                    []

            }


            self._save(
                data
            )



    # =====================================================
    # SAVE
    # =====================================================

    def _save(
        self,
        data
    ):

        with open(
            self.version_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )



    # =====================================================
    # LOAD
    # =====================================================

    def load(self):

        with open(
            self.version_file,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)



    # =====================================================
    # REGISTER RELEASE
    # =====================================================

    def register(
        self,
        version,
        title,
        changes
    ):

        data = self.load()


        release = {

            "version":
                version,

            "title":
                title,

            "changes":
                changes,

            "timestamp":
                datetime.utcnow().isoformat()

        }


        data["history"].append(
            release
        )


        data["current_version"] = (
            version
        )


        self._save(
            data
        )


        return release



    # =====================================================
    # CURRENT
    # =====================================================

    def current(self):

        data = self.load()

        return {

            "system":
                data["system"],

            "version":
                data["current_version"]

        }



    # =====================================================
    # HISTORY
    # =====================================================

    def history(self):

        return self.load()["history"]

