from dataclasses import dataclass
from datetime import datetime

from graph30.constants import PRIORITY


@dataclass
class RedmineTask:
    id: int
    subject: str
    estimated_hours: float
    responsible_lastname: str
    group: str
    quarter: str
    tracker: str
    status: str
    d_create: datetime
    priority_id: int

    @property
    def priority(self) -> str:
        return PRIORITY.get(self.priority_id, f"priority {self.priority_id} can't translate")
