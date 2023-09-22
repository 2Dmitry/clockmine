from typing import TYPE_CHECKING, Optional

import isodate
from clockify.session import ClockifySession  # TODO https://clockify-cli.netlify.app/
from redminelib import Redmine
from tabulate import tabulate

from constants import redmine_url_time_entry
from models import TimeEntry

if TYPE_CHECKING:
    from clockify.session import ClockifySession
    from redminelib import Redmine

    from models import TimeEntry


def get_clockify_tags_map(clockify: "ClockifySession", clockify_workspace_id: str) -> dict[str, str]:
    """Вернет словарь, где ключ - это строка в формате '648f1d8cabc41f2c318b5768', значение - 'Разработка'"""
    return {tag.id_: tag.name for tag in clockify.tag.get_tags(clockify_workspace_id)}


def get_rm_activities(redmine: "Redmine") -> dict:
    res = {}
    for data in redmine.enumeration.filter(resource="time_entry_activities").values():
        res[data["name"]] = data["id"]
    return res


def secs_to_hours(secs: float) -> float:
    return round(secs / 3600, 2)


def collect_data(
    clockify: "ClockifySession", redmine: "Redmine", coeff: Optional[float] = None, target: Optional[float] = None
) -> None:
    clockify_user = clockify.get_current_user()
    clockify_workspace_id = clockify_user.active_workspace
    clockify_tags_map = get_clockify_tags_map(clockify, clockify_workspace_id) if clockify_workspace_id else dict()
    redmine_user_id = redmine.user.get("current").id

    for clockify_time_entry in clockify.time_entry.get_time_entries(clockify_workspace_id, clockify_user.id_):
        description = clockify_time_entry.description[:70]
        hours = secs_to_hours(isodate.parse_duration(clockify_time_entry.time_interval.duration).total_seconds())
        clockify_tag_ids = clockify_time_entry.tag_ids
        rm_activity_name = clockify_tags_map.get(clockify_tag_ids[0]) if clockify_tag_ids else "Разработка"

        TimeEntry(
            user_id=redmine_user_id,
            description=description,
            hours=hours,
            rm_activity_name=rm_activity_name,  # TODO обработать ситуацию, когда юзер указал больше 1 деятельности в Клокифу
        )

    valid_coeff = None
    if target is not None and 0 < target:
        valid_coeff = target / TimeEntry.get_absolute_time()
    elif coeff is not None and 0 < coeff:
        valid_coeff = coeff

    if valid_coeff:
        for te in TimeEntry.get_time_entries().values():
            te.hours *= valid_coeff
        TimeEntry._absolute_time *= valid_coeff

    return


def report() -> None:
    table = [time_entry.get_report_data for time_entry in TimeEntry.get_time_entries().values()]
    table.sort(key=lambda i: (i[0], i[2]), reverse=True)
    print(
        tabulate(
            table,
            headers=("№", "Можно затрекать", "Тема", "Время", "Деятельность", "Дата", "Комментарий"),
            tablefmt="rounded_outline",
            numalign="decimal",
            floatfmt=".2f",
            showindex="always",
        ),
    )
    print(TimeEntry.get_absolute_time())
    return


def push(redmine: "Redmine") -> None:
    for time_entry in TimeEntry.get_time_entries().values():
        time_entry.push_to_redmine(redmine)
    print("Внимание! Удалите вручную записи в Клокифае!")  # TODO добавить удаление времени из Клокифай
    print(f"Посмотреть затреканное время за текущую неделю можно тут: {redmine_url_time_entry}")
    return


def report_push(redmine: "Redmine") -> None:
    report()
    push(redmine)
    return
