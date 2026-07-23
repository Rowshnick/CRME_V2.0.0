import os
import json


class Indexer:

    def __init__(self, base_path):
        self.base_path = base_path
        self.index_path = os.path.join(
            base_path,
            "memory",
            "index.json"
        )

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        if not os.path.exists(self.index_path):
            self.index = {
                "objects": [],
                "relations": [],
                "sessions": [],
                "projects": []
            }
            self._save()
        else:
            self.index = self.load_index()

    # ==========================================
    # Load Index
    # ==========================================
    def load_index(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ==========================================
    # Save Index
    # ==========================================
    def save_index(self, index=None):
        if index is not None:
            self.index = index

        self._save()

    # ==========================================
    # Add Object
    # ==========================================
    def add_object(self, obj):
        self.index["objects"].append(obj.to_dict())
        self._save()

    # ==========================================
    # Add Relation
    # ==========================================
    def add_relation(self, from_id, to_id, relation_type="leads_to"):

        self.index["relations"].append(
            {
                "from": from_id,
                "to": to_id,
                "type": relation_type
            }
        )

        self._save()

    # ==========================================
    # Add Session
    # ==========================================
    def add_session(self, session):

        self.index.setdefault("sessions", [])
        self.index["sessions"].append(session)

        self._save()

    # ==========================================
    # Statistics
    # ==========================================
    def stats(self):

        return {
            "objects": len(self.index.get("objects", [])),
            "relations": len(self.index.get("relations", [])),
            "sessions": len(self.index.get("sessions", [])),
            "projects": len(self.index.get("projects", []))
        }

    # ==========================================
    # Internal Save
    # ==========================================
    def _save(self):

        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(
                self.index,
                f,
                indent=2,
                ensure_ascii=False
            )


