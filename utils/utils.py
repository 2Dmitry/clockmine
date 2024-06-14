import re
from typing import Optional, Union


def hours_convert_to_humanize_hours(time: Union[float, int]) -> Optional[str]:
    hours = int(time)
    minutes = int((time - hours) * 60)
    return f"{hours}h {minutes}m"


def extract_id_from_desc(desc: str) -> Optional[str]:
    for chunk in re.findall(r"\d+", desc):
        if chunk.isdigit():
            return chunk


def extract_comment_from_desc(desc: str) -> str:
    res = ""
    for chunk in desc.split("-ci")[1:]:
        res += chunk.strip()
    return res


def extract_title(desc: str) -> str:
    _ = desc.split("-ci")
    return _[0] if _ else ""
