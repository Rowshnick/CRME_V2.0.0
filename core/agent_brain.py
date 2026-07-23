class AgentBrain:
    def __init__(self, index):
        self.index = index

    def decide(self, text):
        text_l = text.lower()

        if "goal" in text_l or "build" in text_l:
            return {"type": "Goal", "store": True}

        if "fix" in text_l or "bug" in text_l:
            return {"type": "Task", "store": True}

        if "decide" in text_l:
            return {"type": "Decision", "store": True}

        return {"type": "Note", "store": False}

