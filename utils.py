from typing import TYPE_CHECKING

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


def secs_to_hours(secs: float, coeff: float = 1.0) -> float:
    # TODO не умножать здесь на coeff делать это там же где работаем с переменно target, тип if/elif
    return round(secs / 60 / 60 * coeff, 2)


def collect_data(clockify: "ClockifySession", redmine: "Redmine", coeff: float = 1.0, target: float = 0.0) -> None:
    clockify_user = clockify.get_current_user()
    clockify_user_id = clockify_user.id_
    clockify_workspace_id = clockify_user.active_workspace
    clockify_tags_map = get_clockify_tags_map(clockify, clockify_workspace_id) if clockify_workspace_id else dict()
    redmine_user_id = redmine.user.get("current").id

    for clockify_time_entry in clockify.time_entry.get_time_entries(clockify_workspace_id, clockify_user_id):
        clockify_tag_ids = clockify_time_entry.tag_ids or ["Разработка"]

        TimeEntry(
            user_id=redmine_user_id,
            description=clockify_time_entry.description[:60],
            hours=secs_to_hours(
                isodate.parse_duration(clockify_time_entry.time_interval.duration).total_seconds(), coeff=coeff
            ),
            rm_activity_name=clockify_tags_map.get(
                clockify_tag_ids[0], "Разработка"
            ),  # TODO обработать ситуацию, когда юзер указал больше 1 деятельности в Клокифу
        )

    if target != 0:
        coeff = target / TimeEntry.get_absolute_time()
        for te in TimeEntry.get_time_entries().values():
            te.hours *= coeff

    return


def report() -> None:
    table = [time_entry.get_report_data for time_entry in TimeEntry.get_time_entries().values()]
    table.sort(key=lambda i: (i[0], i[2]), reverse=True)
    print(
        tabulate(
            table,
            headers=("№", "Тема", "Время", "Деятельность", "Дата", "Комментарий"),
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


def report_push(redmine: "Redmine") -> None:
    report()
    push(redmine)
