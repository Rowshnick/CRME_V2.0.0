import math


class MemoryIntelligence:
    def __init__(self, index):
        self.index = index

    # -------------------------
    # SCORE OBJECTS
    # -------------------------
    def score_object(self, obj):
        score = 0.5

        content = obj.get("content", "").lower()

        # rule 1: keyword importance
        if "goal" in content:
            score += 0.2

        if "decision" in content:
            score += 0.3

        if "next" in content or "task" in content:
            score += 0.1

        # rule 2: relation importance
        rel_count = len(obj.get("relations", {}).get("leads_to", []))
        score += min(rel_count * 0.05, 0.2)

        # clamp
        return min(score, 1.0)

    # -------------------------
    # APPLY SCORING
    # -------------------------
    def apply_scoring(self):
        for obj in self.index.get("objects", []):
            obj["importance"] = self.score_object(obj)

        return self.index

    # -------------------------
    # RANK OBJECTS
    # -------------------------
    def rank(self):
        return sorted(
            self.index.get("objects", []),
            key=lambda x: x.get("importance", 0),
            reverse=True
        )

    # -------------------------
    # SMART CONTEXT SUMMARY
    # -------------------------
    def summarize(self, top_k=5):
        ranked = self.rank()

        return {
            "key_insights": [
                {
                    "type": o["type"],
                    "content": o["content"],
                    "importance": o.get("importance", 0)
                }
                for o in ranked[:top_k]
            ]
        }



