import time

from core.agent_brain import AgentBrain
from core.auto_memory import AutoMemory
from core.indexer import Indexer
from core.session_engine import SessionEngine


class AutonomousLoop:
    def __init__(self, base_path):
        self.base_path = base_path

        self.indexer = Indexer(base_path)
        self.index = self.indexer.load_index()

        self.brain = AgentBrain(self.index)
        self.auto = AutoMemory(self.index, self.brain)
        self.session_engine = SessionEngine(base_path)

        self.running = False

    # -----------------------------
    # CORE LOOP
    # -----------------------------
    def process_event(self, text):
        decision = self.brain.decide(text)

        if decision["store"]:
            obj = {
                "type": decision["type"],
                "content": text,
                "auto_generated": True
            }

            self.index["objects"].append(obj)
            self.indexer.save(self.index)

            self.session_engine.update_last_session(obj)

            return {"stored": True, "object": obj}

        return {"stored": False}

    # -----------------------------
    # LOOP RUNNER
    # -----------------------------
    def run(self, stream=None, interval=2):
        """
        stream = list of incoming events (simulate or real input)
        """
        self.running = True

        print("\n🧠 AUTONOMOUS LOOP STARTED\n")

        while self.running:

            if stream:
                if len(stream) == 0:
                    break

                text = stream.pop(0)
            else:
                # fallback demo input
                text = "system idle heartbeat"

            result = self.process_event(text)

            print("EVENT:", text)
            print("RESULT:", result)

            time.sleep(interval)

    # -----------------------------
    # STOP LOOP
    # -----------------------------
    def stop(self):
        self.running = False

