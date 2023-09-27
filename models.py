from datetime import date, datetime
from functools import cached_property
from typing import Optional

import requests
from clockify.config import BASE_URL
from clockify.session import ClockifySession
from redminelib import Redmine

from config import CLOCKIFY_API_KEY


class MyRedmine(Redmine):
    @cached_property
    def current_user(self):
        user = self.user.get("current")
        if user:
            return user
        else:
            raise Exception("Не смог получить текущего Redmine-юзера")

    @cached_property
    def current_user_id(self) -> int:
        if self.current_user and self.current_user.id:
            return self.current_user.id
        else:
            raise Exception("User's Id not found.")

    @cached_property
    def time_entry_activities(self) -> dict[str, int]:
        res = {}
        for data in self.enumeration.filter(resource="time_entry_activities").values():
            res[data["name"]] = data["id"]
        return res


class MyClockifySession(ClockifySession):
    def __init__(self, key: str) -> None:
        super().__init__(key)
        self.stop_timer()

    def stop_timer(self) -> None:
        # Stop timer
        session = requests.Session()
        session.headers.update({"x-api-key": CLOCKIFY_API_KEY})
        session.patch(
            url=f"{BASE_URL}/workspaces/{self.workspace_id}/user/{self.current_user_id}/time-entries",
            json={"end": datetime.now().replace(microsecond=0).isoformat() + "Z"},
        )

    @cached_property
    def current_user(self):
        current_user = self.get_current_user()

        if current_user:
            return current_user
        else:
            raise Exception("User not found.")

    @cached_property
    def current_user_id(self) -> str:
        if self.current_user and self.current_user.id_:
            return self.current_user.id_
        else:
            raise Exception("User's Id not found.")

    @cached_property
    def workspace_id(self) -> str:
        if self.current_user and self.current_user.active_workspace:
            return self.current_user.active_workspace
        else:
            raise Exception("User's active-workspace id not found.")

    def time_entries(self):
        return (
            self.time_entry.get_time_entries(user_id=self.current_user_id, workspace_id=self.workspace_id)
            if self.current_user_id and self.workspace_id
            else []
        )

    def tags(self):
        return self.tag.get_tags(self.workspace_id) if self.workspace_id else []

    def tags_map(self) -> dict[str, str]:
        return {tag.id_: tag.name for tag in self.tags()}


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

    def push_to_redmine(self, redmine: "MyRedmine") -> None:
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
