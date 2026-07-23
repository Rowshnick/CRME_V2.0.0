from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DatasetMetadata:
    name: str
    version: str
    source: str
    description: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    size: int = 0
    features: list = field(default_factory=list)
    labels: list = field(default_factory=list)


@dataclass
class DatasetRecord:

    metadata: DatasetMetadata
    path: str

    statistics: dict = field(
        default_factory=dict
    )

    schema: dict = field(
        default_factory=dict
    )

