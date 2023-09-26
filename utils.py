from typing import TYPE_CHECKING, Optional

import dateutil.parser
import isodate
import requests
from clockify.config import BASE_URL
from dateutil import tz
from tabulate import tabulate

from config import CLOCKIFY_API_KEY, TIMEZONE
from constants import redmine_url_time_entry
from models import MyClockifySession, TimeEntry

if TYPE_CHECKING:
    from redminelib import Redmine


def get_rm_activities(redmine: "Redmine") -> dict[str, int]:
    res = {}
    for data in redmine.enumeration.filter(resource="time_entry_activities").values():
        res[data["name"]] = data["id"]
    return res


def secs_to_hours(secs: float) -> float:
    return round(secs / 3600, 2)


def collect_data(
    clockify: "MyClockifySession", redmine: "Redmine", coeff: Optional[float] = None, target: Optional[float] = None
) -> None:
    redmine_user_id = redmine.user.get("current").id
    if not redmine_user_id:
        raise Exception("Не смог получить активное Redmine-юзера")

    # Parse
    clockify_tags_map = clockify.tags_map()
    for clockify_time_entry in clockify.time_entries():
        rm_activity_name = "Разработка"
        if tag_ids := clockify_time_entry.tag_ids:
            rm_activity_name = clockify_tags_map[tag_ids[0]]

        TimeEntry(
            user_id=redmine_user_id,
            spent_on=dateutil.parser.isoparse(clockify_time_entry.time_interval.start)
            .astimezone(tz.gettz(TIMEZONE))
            .date(),
            description=clockify_time_entry.description[:70],
            hours=secs_to_hours(isodate.parse_duration(clockify_time_entry.time_interval.duration).total_seconds()),
            rm_activity_name=rm_activity_name,
            rm_activity_id=get_rm_activities(redmine).get(rm_activity_name),
        )
        TimeEntry.clockify_ids.append(clockify_time_entry.id_)

    # Accept coeff
    valid_coeff = None
    if target is not None and 0 < target:
        valid_coeff = target / TimeEntry.get_absolute_time()
    elif coeff is not None and 0 < coeff:
        valid_coeff = coeff

    if valid_coeff:
        for te in TimeEntry.get_time_entries().values():
            te.hours *= valid_coeff
        TimeEntry._absolute_time *= valid_coeff


def report() -> None:
    table = [time_entry.get_report_data for time_entry in TimeEntry.get_time_entries().values()]
    table.sort(key=lambda i: (i[0], i[2]), reverse=True)
    print(
        tabulate(
            table,
            headers=(
                "№ задачи",
                "Можно затрекать",
                "Тема/Описание",
                "Время",
                "Деятельность",
                "Дата",
                "Комментарий",
            ),
            tablefmt="rounded_outline",
            numalign="decimal",
            floatfmt=".2f",
            showindex="always",
        ),
    )
    print(TimeEntry.get_absolute_time())


def push(clockify: "MyClockifySession", redmine: "Redmine") -> None:
    # Push
    for time_entry in TimeEntry.get_time_entries().values():
        if not time_entry.can_push_to_redmine:
            raise Exception(
                f"Some attributes are required. Check time entry '{time_entry.description}' and restart the command."
            )

    for time_entry in TimeEntry.get_time_entries().values():
        time_entry.push_to_redmine(redmine)

    # Delete
    session = requests.Session()
    session.headers.update({"x-api-key": CLOCKIFY_API_KEY})
    if TimeEntry.clockify_ids:
        res = session.delete(
            url=f"{BASE_URL}/workspaces/{clockify.workspace_id}/user/{clockify.current_user_id}/time-entries",
            params={"time-entry-ids": TimeEntry.clockify_ids},
        )
        if res.status_code != 200:
            print(
                "Can't clear Clockify.", requests.HTTPError(f"HTTP ERROR {res.status_code}: {res.reason} - {res.text}")
            )

    print(f"Посмотреть затреканное время за текущую неделю можно тут: {redmine_url_time_entry}")
