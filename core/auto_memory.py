class AutoMemory:
    def __init__(self, index, brain):
        self.index = index
        self.brain = brain

    def process(self, text):
        decision = self.brain.decide(text)

        if not decision["store"]:
            return None

        return {
            "type": decision["type"],
            "content": text,
            "auto_generated": True
        }

