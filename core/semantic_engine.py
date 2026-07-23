class SemanticEngine:
    def __init__(self, index):
        self.index = index

    # -------------------------
    # SIMPLE SEMANTIC SEARCH
    # -------------------------
    def find_similar(self, text, threshold=0.2):
        results = []

        for o in self.index.get("objects", []):
            content = o.get("content", "").lower()

            # very simple semantic approximation
            score = self._similarity(text.lower(), content)

            if score >= threshold:
                results.append({
                    "object": o,
                    "score": score
                })

        return sorted(results, key=lambda x: x["score"], reverse=True)

    # -------------------------
    # CLUSTERING BY TYPE
    # -------------------------
    def cluster_by_type(self):
        clusters = {}

        for o in self.index.get("objects", []):
            t = o.get("type", "Unknown")
            clusters.setdefault(t, []).append(o)

        return clusters

    # -------------------------
    # SIMPLE SIMILARITY FUNCTION
    # -------------------------
    def _similarity(self, a, b):
        a_words = set(a.split())
        b_words = set(b.split())

        if not a_words or not b_words:
            return 0.0

        intersection = a_words.intersection(b_words)
        union = a_words.union(b_words)

        return len(intersection) / len(union)

