from functools import cached_property
from typing import TYPE_CHECKING, Optional

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
        return {_["name"]: _["id"] for _ in self.enumeration.filter(resource="time_entry_activities").values()}

    @cached_property
    def young_issue_id(self) -> Optional[int]:
        id = None
        for issue in self.issue.all(sort="id:desc", limit=1):
            id = issue.id
        return id

    @cached_property
    def old_issue_id(self) -> Optional[int]:
        id = None
        for issue in self.issue.all(sort="id:asc", limit=1):
            id = issue.id
        return id