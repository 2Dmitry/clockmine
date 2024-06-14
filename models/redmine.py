from functools import cached_property
from typing import TYPE_CHECKING

from redminelib import Redmine

if TYPE_CHECKING:
    from redminelib.resources.standard import User as RmUser


class MyRedmine(Redmine):
    @cached_property
    def current_user(self) -> "RmUser":
        if user := self.auth():
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
        return {
            activity["name"]: activity["id"]
            for activity in self.enumeration.filter(resource="time_entry_activities").values()
        }
