from datetime import date
from functools import cached_property
from typing import Optional

from config import REDMINE_URL
from models import redmine
from utils.utils import extract_id_from_desc, hours_convert_to_humanize_hours


class TimeEntry:
    _absolute_time = 0.0
    _all = dict()
    clockify_ids = []

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} {self.issue_id or 'None'} {self.rm_activity_name or 'None'}>"

    def __init__(
        self,
        description: str,
        user_id: Optional[int],
        rm_activity_id: Optional[int],
        spent_on: date,
        hours: float,
        rm_activity_name: str = "Разработка",
        comments: str = "",
    ) -> None:
        self.description = description.strip()
        self.issue_id = extract_id_from_desc(self.description) or ""
        self.hours = hours
        TimeEntry._absolute_time = round(TimeEntry.get_absolute_time + self.hours, 2)
        self.rm_activity_name = rm_activity_name
        self.rm_activity_id = rm_activity_id
        self.spent_on = spent_on
        self.user_id = user_id
        self.comments = comments  # TODO В клокиефае нет комментариев

        key = (
            (self.issue_id, self.rm_activity_name)
            if self.issue_id
            else (self.issue_id, self.rm_activity_name, self.description)
        )
        if _ := TimeEntry._all.get(key):
            _.hours += self.hours
        else:
            TimeEntry._all[key] = self

    @classmethod
    @property
    def get_absolute_time(cls) -> float:
        return cls._absolute_time

    @classmethod
    @property
    def get_time_entries(cls) -> dict[tuple[str, str], "TimeEntry"]:
        return cls._all

    @cached_property
    def has_access_to_issue(self) -> bool:
        try:
            redmine.issue.get(self.issue_id)
            return True
        except Exception:
            print(
                f"ERROR! У вас нет доступа в Redmine к задаче #{self.issue_id} ({self.description} - {self.hours})\n{REDMINE_URL + 'issues/' + self.issue_id}.\nДоступный диапазон задач для вас: с {redmine.old_issue_id} по {redmine.young_issue_id}\nP.S.Некоторые задачи внутри диапазона тоже недоступны, если вы не Степа.\n"
            )
            return False

    @property
    def can_push_to_redmine(self) -> bool:
        return all(
            (
                self.has_access_to_issue,
                self.spent_on,
                0 < self.hours,
                self.rm_activity_id,
                self.user_id,
            )
        )

    @property
    def push_to_redmine(self) -> None:
        redmine.time_entry.create(
            issue_id=self.issue_id,
            spent_on=self.spent_on,
            hours=self.hours,
            activity_id=self.rm_activity_id,
            user_id=self.user_id,
            comments=self.comments,
        )

    @property
    def get_report_data(self) -> tuple:
        desc = self.get_rm_issue_subject or self.description
        return (
            {True: "yes", False: "no"}.get(self.can_push_to_redmine),
            self.issue_id,
            desc[:60],
            f"{hours_convert_to_humanize_hours(self.hours)} ({round(self.hours, 2)}h)",
            self.rm_activity_name,
            self.spent_on.strftime("%d %B"),
            # self.comments,
        )

    @property
    def get_rm_issue_subject(self) -> Optional[str]:
        return issue.subject if self.has_access_to_issue and (issue := redmine.issue.get(self.issue_id)) else None
