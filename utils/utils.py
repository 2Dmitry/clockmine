import re
from typing import Optional, Union

from models import redmine


def hours_convert_to_humanize_hours(time: Union[float, int]) -> Optional[str]:
    if time:
        hours = int(time)
        minutes = int((time - hours) * 60)
        return f"{hours}h {minutes}m"


def extract_digit_from_desc(desc: str) -> Optional[str]:
    _ = re.findall(r"\d+", desc)
    for chunk in _:
        if chunk.isdigit():
            return chunk


def extract_id_from_desc(desc: str) -> Optional[str]:
    _ = re.findall(r"\d+", desc)
    for chunk in _:
        if (
            chunk.isdigit()
            and redmine.young_issue_id
            and redmine.old_issue_id
            and (redmine.old_issue_id <= int(chunk) <= redmine.young_issue_id)
        ):
            return chunk
