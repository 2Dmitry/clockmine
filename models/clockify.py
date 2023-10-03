from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING

from clockify.config import BASE_URL
from clockify.model.tag_model import Tag
from clockify.session import ClockifySession

if TYPE_CHECKING:
    from clockify.model.time_entry_model import TimeEntry as CfyTimeEntry
    from clockify.model.user_model import User as CfyUser


class MyClockify(ClockifySession):
    def __init__(self, key: str) -> None:
        super().__init__(key)
        self.stop_timer()

    def stop_timer(self) -> None:
        # Stop timer
        self.session.patch(
            url=f"{BASE_URL}/workspaces/{self.workspace_id}/user/{self.current_user_id}/time-entries",
            json={"end": datetime.now().replace(microsecond=0).isoformat() + "Z"},
        )

    @cached_property
    def current_user(self) -> "CfyUser":
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

    def time_entries(self) -> list["CfyTimeEntry"]:
        return (
            self.time_entry.get_time_entries(user_id=self.current_user_id, workspace_id=self.workspace_id)
            if self.current_user_id and self.workspace_id
            else []
        )

    def tags(self) -> list[Tag]:
        return self.tag.get_tags(self.workspace_id) if self.workspace_id else []

    def tags_map(self) -> dict[str, str]:
        return {tag.id_: tag.name for tag in self.tags()}

    def create_tag(self, tag_name: str) -> None:
        self.tag.create_tag(Tag(name=tag_name, workspace_id=self.workspace_id))

    def delete_tag(self, tag_id: str) -> None:
        self.tag.delete_tag(workspace_id=self.workspace_id, tag_id=tag_id)
