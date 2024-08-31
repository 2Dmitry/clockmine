from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from graph30.constants import COLORS, GROUP_MAP, PRIORITY, QUARTER_MAP
from graph30 import QUARTER


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
    responsible_lastname: str
    kpi: bool
    quarter: str
    group: str
    priority_id: int
    tracker: str
    status: str
    d_create: datetime
    project_id: int

    @property
    def priority(self) -> str:
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
    def asap(self) -> Literal["ASAP"] | Literal[""]:
        return "ASAP" if self.kpi else ""

    @property
    def node_label(self):
        return f"{self.code} | {self.quarter}\n{self.asap} {self.group} {self.priority}\n{self.id} {self.tracker}\n{self.status}\n{self.responsible_lastname or '---'}"

    @property
    def node_color(self) -> str:
        color = ""
        if self.project_id == 69:
            if self.quarter == QUARTER:
                color = COLORS.get(self.status, "")
            else:
                color = COLORS.get("Выполнена", "")
        else:
            color = COLORS.get(self.status, "")
        return color
