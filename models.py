from datetime import datetime
from typing import TYPE_CHECKING

from constants import redmine_activities_map

if TYPE_CHECKING:
    from redminelib import Redmine


class TimeEntry:
    absolute_time = 0.0

    def __init__(
        self,
        issue_id=None,
        description="",
        hours=0.0,
        rm_activity_name="Разработка",
        spent_on=datetime.today().date(),
        user_id=None,
        comments="",
    ):
        self.issue_id = issue_id
        self.description = description
        self.hours = hours
        TimeEntry.absolute_time = round(TimeEntry.absolute_time + hours, 2)
        self.rm_activity_name = rm_activity_name
        self.activity_id = redmine_activities_map.get(self.rm_activity_name)
        self.spent_on = spent_on
        self.user_id = user_id
        self.comments = comments

        for chunk in self.description.split(" "):
            if "#" in chunk:
                self.issue_id = chunk[1:]
                break

    @property
    def can_push_to_redmine(self) -> bool:
        return all((self.issue_id, self.spent_on, self.hours, self.activity_id, self.user_id))

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
            raise ValueError(f"Some attributes are required. Check time entry {self.description}")

    @property
    def relative_time(self) -> float:
        return round(self.hours / self.absolute_time * 100, 1)

    def get_report_data(self) -> tuple:
        return (
            self.issue_id,
            self.description,
            self.hours,  # TODO f"{self.hours} из {self.absolute_time} ({self.relative_time}%)",
            self.rm_activity_name,
            self.spent_on,
            self.comments,
        )
