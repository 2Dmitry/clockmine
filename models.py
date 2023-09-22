from datetime import date, timedelta
from typing import TYPE_CHECKING, Optional

from constants import redmine_activities_map

if TYPE_CHECKING:
    from redminelib import Redmine


class TimeEntry:
    _absolute_time = 0.0  # TODO FIX плохой нейминг
    _all = dict()  # TODO FIX плохой нейминг

    def __init__(
        self,
        description: str,
        user_id: Optional[int],
        hours: float = 0.0,
        rm_activity_name: str = "Разработка",
        spent_on: date = date.today(),  # - timedelta(days=1), # TODO парсить дату из Клокифу
        comments: str = "",
    ):
        self.description = description
        self.issue_id = self.extract_id_from_desc(self.description)
        self.hours = hours
        TimeEntry._absolute_time = round(TimeEntry.get_absolute_time() + self.hours, 2)
        self.rm_activity_name = rm_activity_name
        self.activity_id = redmine_activities_map.get(self.rm_activity_name)
        self.spent_on = spent_on
        self.user_id = user_id
        self.comments = comments  # TODO В клокиефае нет комментариев, можно писать коммент в описании и потом парсить

        key = (self.issue_id, self.rm_activity_name)
        if _ := TimeEntry._all.get(key):
            _.hours += self.hours
        else:
            TimeEntry._all[key] = self

    def extract_id_from_desc(self, desc: str) -> str:
        id = desc or ""
        for chunk in desc.split(" "):
            if "#" in chunk:
                id = chunk[1:]
                break
        return id

    @classmethod
    def get_absolute_time(cls) -> float:
        return cls._absolute_time

    @classmethod
    def get_time_entries(cls) -> dict[tuple[str, str], "TimeEntry"]:  # TODO fix эту дичь
        return cls._all

    @property
    def can_push_to_redmine(self) -> bool:
        return all(
            (self.issue_id, self.issue_id.isdigit(), self.spent_on, 0 < self.hours, self.activity_id, self.user_id)
        )

    def push_to_redmine(self, redmine: "Redmine") -> None:
        if self.can_push_to_redmine:
            redmine.time_entry.create(
                issue_id=self.issue_id,
                spent_on=self.spent_on,
                hours=self.hours,
                activity_id=self.activity_id,
                user_id=self.user_id,
                comments=self.comments,
            )
        else:
            raise Exception(f"Some attributes are required. Check time entry '{self.description}'")
        return

    @property
    def relative_time(self) -> float:
        return round(self.hours / self.get_absolute_time() * 100, 1)

    @property
    def get_report_data(self) -> tuple:
        return (
            self.issue_id,
            self.can_push_to_redmine,
            self.description,
            self.hours,  # TODO f"{self.hours} из {self.absolute_time} ({self.relative_time}%)",
            self.rm_activity_name,
            self.spent_on,
            self.comments,
        )
