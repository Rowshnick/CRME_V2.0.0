import math


class EvaluationMetrics:
    """
    CRME Evaluation Metrics Engine

    Calculates research evaluation metrics:

    - Memory Construction Score (MCS)
    - Semantic Retrieval Score (SRS)
    - Knowledge Graph Quality (KGQ)
    - Research Reproducibility Score (RRS)
    - CRME Evaluation Score (CES)
    """


    def __init__(self):

        self.weights = {

            "mcs": 0.25,
            "srs": 0.25,
            "kgq": 0.25,
            "rrs": 0.25

        }



    # ===============================================
    # Memory Construction Score
    # ===============================================

    def memory_construction_score(
        self,
        memories,
        artifacts,
        ledger_entries
    ):

        if memories == 0:
            return 0.0


        score = (

            0.5 *

            min(
                memories / 100,
                1
            )

            +

            0.25 *

            min(
                artifacts / 50,
                1
            )

            +

            0.25 *

            min(
                ledger_entries / 100,
                1
            )

        )


        return round(
            score * 100,
            2
        )



    # ===============================================
    # Semantic Retrieval Score
    # ===============================================

    def semantic_retrieval_score(
        self,
        retrieved,
        relevant
    ):

        if relevant == 0:
            return 0.0


        score = (
            retrieved /
            relevant
        )


        return round(
            min(score, 1) * 100,
            2
        )



    # ===============================================
    # Knowledge Graph Quality
    # ===============================================

    def knowledge_graph_quality(
        self,
        nodes,
        relations
    ):

        if nodes == 0:
            return 0.0


        density = (
            relations /
            nodes
        )


        score = min(
            density / 5,
            1
        )


        return round(
            score * 100,
            2
        )



    # ===============================================
    # Research Reproducibility Score
    # ===============================================

    def reproducibility_score(
        self,
        sessions,
        decisions,
        provenance
    ):

        values = [

            min(
                sessions / 20,
                1
            ),

            min(
                decisions / 50,
                1
            ),

            min(
                provenance / 50,
                1
            )

        ]


        score = sum(values) / len(values)


        return round(
            score * 100,
            2
        )



    # ===============================================
    # CES
    # ===============================================

    def calculate_ces(
        self,
        metrics
    ):

        ces = (

            metrics["mcs"]
            *
            self.weights["mcs"]

            +

            metrics["srs"]
            *
            self.weights["srs"]

            +

            metrics["kgq"]
            *
            self.weights["kgq"]

            +

            metrics["rrs"]
            *
            self.weights["rrs"]

        )


        return round(
            ces,
            2
        )



    # ===============================================
    # Full Evaluation
    # ===============================================

    def evaluate(
        self,
        data
    ):


        metrics = {


            "mcs":
            self.memory_construction_score(

                data.get(
                    "memories",
                    0
                ),

                data.get(
                    "artifacts",
                    0
                ),

                data.get(
                    "ledger_entries",
                    0
                )

            ),



            "srs":
            self.semantic_retrieval_score(

                data.get(
                    "retrieved",
                    0
                ),

                data.get(
                    "relevant",
                    0
                )

            ),



            "kgq":
            self.knowledge_graph_quality(

                data.get(
                    "knowledge_nodes",
                    0
                ),

                data.get(
                    "relations",
                    0
                )

            ),



            "rrs":
            self.reproducibility_score(

                data.get(
                    "sessions",
                    0
                ),

                data.get(
                    "decisions",
                    0
                ),

                data.get(
                    "provenance",
                    0
                )

            )

        }


        metrics["ces"] = self.calculate_ces(
            metrics
        )


        return metrics

