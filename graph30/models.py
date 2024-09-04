from dataclasses import dataclass
from datetime import datetime, date
from typing import Literal, Optional

from graph30.constants import COLORS, GROUP_MAP, PRIORITY, QUARTER_MAP


class RedmineTaskUtils:
    @classmethod
    def get_group_int(cls, group) -> int:
        group = GROUP_MAP.get(group)

        if not isinstance(group, int):
            group = 1
            # raise Exception

        return group

    @classmethod
    def get_quarter_int(cls, quarter) -> int:
        quarter = QUARTER_MAP.get(quarter)

        if not isinstance(quarter, int):
            quarter = 1
            # raise Exception

        return quarter

    @classmethod
    def translate_priority_id(cls, priority_id):
        return PRIORITY.get(priority_id, f"priority {priority_id} can't translate")


@dataclass
class RedmineTask:
    id: int
    subject: str
    estimated_hours: float
    author_lastname: str
    kpi: bool
    quarter: str
    group: str
    priority_id: int
    tracker: str
    status: str
    d_create: datetime
    project_id: int
    responsible: str
    executor: str
    due_date: date

    @property
    def responsible_display(self) -> str:
        return self.responsible.split(" ")[0] if self.responsible else "---"

    @property
    def executor_display(self) -> str:
        return self.executor.split(" ")[0] if self.executor else "---"

    @property
    def priority_display(self) -> str:
        return RedmineTaskUtils.translate_priority_id(self.priority_id)

    @property
    def code(self) -> int:
        kpi = self.kpi
        quarter = RedmineTaskUtils.get_quarter_int(self.quarter)
        group = RedmineTaskUtils.get_group_int(self.group)
        priority = self.priority_id

        return kpi * 1000 + quarter * 100 + group * 10 + priority

    @property
    def node_size(self):
        # todo fixme некрасиво
        if self.estimated_hours:
            if self.estimated_hours > 100:
                size = self.estimated_hours / 3
            else:
                size = self.estimated_hours
        else:
            size = 20
        return size

    @property
    def due_date_display(self) -> str:
        return self.due_date.strftime("%d.%m.%Y") if self.due_date else "---"

    @property
    def asap_display(self) -> Literal["ASAP"] | Literal["---"]:
        return "ASAP" if self.kpi else "---"

    @property
    def sign(self) -> str:
        lst = [
            f"{self.due_date_display}",
            f"№ {self.id}",
            f"{self.asap_display} ({self.code})",
            f"{self.status}",
            f"{self.responsible_display} - {self.executor_display}",
        ]
        return "\n".join(lst)

    @property
    def color_display(self) -> Optional[str]:
        color = ""
        if self.project_id == 69:
            color = COLORS.get(self.status, "")

        if (self.quarter != "24_3" or not self.kpi) and self.status != "Ожидает релиз, проверена":
            color = COLORS.get("Выполнена", "")

        return color
