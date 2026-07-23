class MemoryDeduplicator:
    def __init__(self, index):
        self.index = index

    def deduplicate_objects(self):
        seen = set()
        clean = []

        for obj in self.index.get("objects", []):
            key = obj.get("type") + "::" + obj.get("content")

            if key not in seen:
                seen.add(key)
                clean.append(obj)

        self.index["objects"] = clean
        return self.index

    def deduplicate_sessions(self):
        seen = set()
        clean = []

        for s in self.index.get("sessions", []):
            key = s.get("session_id")

            if key and key not in seen:
                seen.add(key)
                clean.append(s)

        self.index["sessions"] = clean
        return self.index

