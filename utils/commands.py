from typing import Optional

import dateutil.parser
import isodate
import requests
from clockify.config import BASE_URL
from dateutil import tz
from tabulate import tabulate

from config import REDMINE_ACTIVITIES_NOT_ALLOWED, REDMINE_URL_TIME_ENTRY, TIMEZONE
from models import clockify, redmine
from models.time_entry import TimeEntry
from utils.utils import hours_convert_to_humanize_hours


def init() -> None:
    for activity_name in redmine.time_entry_activities.keys():
        if activity_name not in clockify.tags_map().values() and activity_name not in REDMINE_ACTIVITIES_NOT_ALLOWED:
            clockify.create_tag(tag_name=activity_name)

    for tag_id, tag_name in clockify.tags_map().items():
        if tag_name not in redmine.time_entry_activities.keys():
            clockify.delete_tag(tag_id=tag_id)

    if len(clockify.tags()) > 3:
        print(
            "INFO. Рекомендуется использовать не больше 3 (трёх) тегов. 4 тега и больше не помещаются в списке тегов в расширении Clockify для браузеров."
        )


def collect_data(coeff: Optional[float] = None, target: Optional[float] = None) -> None:
    def _secs_to_hours(secs: float) -> float:
        return round(secs / 3600, 2)

    # Parse
    clockify_tags_map = clockify.tags_map()
    for clockify_time_entry in clockify.time_entries():
        rm_activity_name = "Разработка"
        if tag_ids := clockify_time_entry.tag_ids:
            rm_activity_name = clockify_tags_map[tag_ids[0]]

        TimeEntry(
            user_id=redmine.current_user_id,
            spent_on=dateutil.parser.isoparse(clockify_time_entry.time_interval.start)
            .astimezone(tz.gettz(TIMEZONE))
            .date(),
            description=clockify_time_entry.description[:70],
            hours=_secs_to_hours(isodate.parse_duration(clockify_time_entry.time_interval.duration).total_seconds()),
            rm_activity_name=rm_activity_name,
            rm_activity_id=redmine.time_entry_activities.get(rm_activity_name, None),
        )
        TimeEntry.clockify_ids.append(clockify_time_entry.id_)

    # Accept coeff
    valid_coeff = None
    if target is not None and 0 < target:
        valid_coeff = target / TimeEntry.get_absolute_time
    elif coeff is not None and 0 < coeff:
        valid_coeff = coeff

    if valid_coeff:
        for te in TimeEntry.get_time_entries.values():
            te.hours *= valid_coeff
        TimeEntry._absolute_time *= valid_coeff


def report() -> None:
    table = [time_entry.get_report_data for time_entry in TimeEntry.get_time_entries.values()]
    table.sort(key=lambda i: (i[1],), reverse=True)
    print(
        tabulate(  # honestly spizjeno from Yonapach <3
            table,
            headers=(
                "Ok?",
                "Task#",
                "Тема/Описание",
                "Время",
                "Деятельность",
                "Дата",
                # "Комментарий",
            ),
            tablefmt="rounded_outline",
            numalign="decimal",
            floatfmt=".2f",
            showindex="always",
        ),
    )
    print(
        "Суммарное затреканное время:",
        hours_convert_to_humanize_hours(TimeEntry.get_absolute_time),
        f"({round(TimeEntry.get_absolute_time, 2)}h)",
    )


def push() -> None:
    # Push
    for time_entry in TimeEntry.get_time_entries.values():
        if not time_entry.can_push_to_redmine:
            raise Exception(
                f"Some attributes are required. Check time entry '{time_entry.description}' and restart the command."
            )

    for time_entry in TimeEntry.get_time_entries.values():
        time_entry.push_to_redmine

    # Delete
    if TimeEntry.clockify_ids:
        res = clockify.session.delete(
            url=f"{BASE_URL}/workspaces/{clockify.workspace_id}/user/{clockify.current_user_id}/time-entries",
            params={"time-entry-ids": TimeEntry.clockify_ids},
        )
        if res.status_code != 200:
            print(
                "Can't clear Clockify.", requests.HTTPError(f"HTTP ERROR {res.status_code}: {res.reason} - {res.text}")
            )

    print(f"Посмотреть затреканное время за текущую неделю можно тут:\n{REDMINE_URL_TIME_ENTRY}")
