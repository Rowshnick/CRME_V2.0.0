import uuid
from datetime import datetime


class MemoryEngine:
    """
    CRME Memory Engine

    Responsibilities:
    - Extract research knowledge from text
    - Create structured memory objects
    - Prepare data for semantic search
    - Feed Project Ledger
    """

    def __init__(
        self,
        text=""
    ):

        self.text = text



    # =====================================================
    # MEMORY EXTRACTION
    # =====================================================

    def extract(self):

        goals = []

        decisions = []

        next_steps = []

        artifacts = []



        for line in self.text.split("\n"):

            clean = line.strip()


            if not clean:
                continue


            l = clean.lower()



            if (
                "goal" in l
                or "هدف" in l
            ):

                goals.append(
                    clean
                )



            if (
                "decision" in l
                or "تصمیم" in l
            ):

                decisions.append(
                    clean
                )



            if (
                "next" in l
                or "بعد" in l
                or "مرحله" in l
            ):

                next_steps.append(
                    clean
                )



            if (
                "file" in l
                or "artifact" in l
                or "فایل" in l
            ):

                artifacts.append(
                    clean
                )



        return {

            "goals":
                goals,

            "decisions":
                decisions,

            "next_steps":
                next_steps,

            "artifacts":
                artifacts

        }



    # =====================================================
    # CREATE MEMORY OBJECT
    # =====================================================

    def create_memory_object(
        self,
        source="session"
    ):


        extracted = self.extract()



        return {


            "memory_id":
                f"M-{uuid.uuid4().hex[:12]}",


            "created_at":
                datetime.utcnow().isoformat(),


            "source":
                source,


            "content":
                self.text,


            "knowledge":
                extracted

        }
