import os
import json
from datetime import datetime
import uuid



class GraphEngine:
    """
    CRME Knowledge Graph Engine

    Features:
    - Memory nodes
    - Goal nodes
    - Decision nodes
    - Relations
    - Persistent storage
    """



    def __init__(
        self,
        storage_path="storage/graph.json"
    ):

        self.storage_path = storage_path


        self.index = {

            "objects": [],

            "relations": []

        }


        self.load()



    # =====================================================
    # ADD MEMORY
    # =====================================================

    def add_memory(
        self,
        memory
    ):


        memory_id = self._id("O")


        memory_object = {

            "id": memory_id,

            "type": "memory",

            "data": memory,

            "created_at":
                datetime.utcnow().isoformat()

        }


        self.index["objects"].append(
            memory_object
        )


        knowledge = memory.get(
            "knowledge",
            {}
        )


        for goal in knowledge.get(
            "goals",
            []
        ):

            self._add_child(
                memory_id,
                "goal",
                {
                    "text": goal
                },
                "contains_goal"
            )



        for decision in knowledge.get(
            "decisions",
            []
        ):

            self._add_child(
                memory_id,
                "decision",
                {
                    "text": decision
                },
                "contains_decision"
            )



        for artifact in knowledge.get(
            "artifacts",
            []
        ):

            self._add_child(
                memory_id,
                "artifact",
                {
                    "text": artifact
                },
                "contains_artifact"
            )


        self.save()


        return memory_id



    # =====================================================
    # ADD CHILD NODE
    # =====================================================

    def _add_child(
        self,
        parent,
        obj_type,
        data,
        relation
    ):


        child_id = self._id("O")


        obj = {

            "id": child_id,

            "type": obj_type,

            "data": data,

            "created_at":
                datetime.utcnow().isoformat()

        }


        self.index["objects"].append(
            obj
        )


        self.index["relations"].append(

            {

                "id":
                    self._id("R"),

                "from":
                    parent,

                "to":
                    child_id,

                "type":
                    relation,

                "created_at":
                    datetime.utcnow().isoformat()

            }

        )



    # =====================================================
    # QUERY
    # =====================================================

    def find_by_type(
        self,
        obj_type
    ):

        return [

            o

            for o in self.index["objects"]

            if o["type"] == obj_type

        ]



    def find_related(
        self,
        object_id
    ):

        return [

            r

            for r in self.index["relations"]

            if
            r["from"] == object_id
            or
            r["to"] == object_id

        ]



    def export(self):

        return self.index



    # =====================================================
    # STORAGE
    # =====================================================

    def save(self):

        directory = os.path.dirname(
            self.storage_path
        )


        if directory:

            os.makedirs(
                directory,
                exist_ok=True
            )


        with open(
            self.storage_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.index,
                f,
                indent=2,
                ensure_ascii=False
            )



    def load(self):

        if not os.path.exists(
            self.storage_path
        ):

            return



        with open(
            self.storage_path,
            "r",
            encoding="utf-8"
        ) as f:

            self.index = json.load(f)



    # =====================================================
    # UTIL
    # =====================================================

    def _id(
        self,
        prefix
    ):

        return (
            f"{prefix}-{uuid.uuid4().hex[:10]}"
        )

