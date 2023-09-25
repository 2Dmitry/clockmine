from datetime import date
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from redminelib import Redmine


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
    ):
        self.description = description
        self.issue_id = self.extract_id_from_desc(self.description)
        self.hours = hours
        TimeEntry._absolute_time = round(TimeEntry.get_absolute_time() + self.hours, 2)
        self.rm_activity_name = rm_activity_name
        self.rm_activity_id = rm_activity_id
        self.spent_on = spent_on
        self.user_id = user_id
        self.comments = comments  # TODO В клокиефае нет комментариев

        key = (self.issue_id, self.rm_activity_name)
        if _ := TimeEntry._all.get(key):
            _.hours += self.hours
        else:
            TimeEntry._all[key] = self

    def extract_id_from_desc(self, desc: str) -> str:
        id = ""
        for chunk in desc.split(" "):
            if "#" in chunk and chunk[1:].isdigit():
                id = chunk[1:]
                break
        return id

    @classmethod
    def get_absolute_time(cls) -> float:
        return cls._absolute_time

    @classmethod
    def get_time_entries(cls) -> dict[tuple[str, str], "TimeEntry"]:
        return cls._all

    @property
    def can_push_to_redmine(self) -> bool:
        return all(
            (
                self.issue_id,
                self.issue_id.isdigit(),
                self.spent_on,
                0 < self.hours,
                self.rm_activity_id,
                self.user_id,
            )
        )

    def push_to_redmine(self, redmine: "Redmine") -> None:
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
        return (
            self.issue_id,
            self.can_push_to_redmine,
            self.description,
            self.hours,
            self.rm_activity_name,
            self.spent_on,
            self.comments,
        )
