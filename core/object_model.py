import uuid
from datetime import datetime


class ResearchObject:
    def __init__(
        self,
        obj_type,
        content,
        project="CRME",
        session_id=None,
        status="draft",
        confidence=0.5,
        tags=None,
        relations=None,
    ):
        self.id = f"CRME-{uuid.uuid4().hex[:8]}"
        self.type = obj_type
        self.project = project
        self.session_id = session_id
        self.timestamp = datetime.now().isoformat()

        self.content = content
        self.status = status
        self.confidence = confidence

        self.tags = tags or []

        self.relations = relations or {
            "parent": [],
            "caused_by": [],
            "leads_to": [],
        }

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "project": self.project,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "content": self.content,
            "status": self.status,
            "confidence": self.confidence,
            "tags": self.tags,
            "relations": self.relations,
        }


