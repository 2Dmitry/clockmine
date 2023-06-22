from typing import TYPE_CHECKING

import isodate
from clockify.session import (
    ClockifySession,  # TODO попробуй https://clockify-cli.netlify.app/
)
from redminelib import Redmine
from tabulate import tabulate

from config import CLOCKIFY_API_KEY, DEBUG_MODE, REDMINE_API_KEY
from constants import redmine_url, redmine_url_time_entry
from models import TimeEntry
from utils import get_clockify_tags_map, secs_to_hours

if TYPE_CHECKING:
    from clockify.session import ClockifySession
    from redminelib import Redmine


def clockify_to_redmine(clockify: "ClockifySession", redmine: "Redmine") -> None:
    clockify_user = clockify.get_current_user()
    clockify_user_id = clockify_user.id_
    clockify_workspace_id = clockify_user.active_workspace
    clockify_tags_map = get_clockify_tags_map(clockify, clockify_workspace_id) if clockify_workspace_id else dict()
    redmine_user_id = redmine.user.get("current").id

    time_entries = dict()

    # Парсим затреканное в Клокифае время
    for clockify_time_entry in clockify.time_entry.get_time_entries(clockify_workspace_id, clockify_user_id):
        clockify_tag_ids = clockify_time_entry.tag_ids or ["Разработка"]

        time_entry = TimeEntry(
            user_id=redmine_user_id,
            description=clockify_time_entry.description[:60],
            hours=secs_to_hours(isodate.parse_duration(clockify_time_entry.time_interval.duration).total_seconds()),
            rm_activity_name=clockify_tags_map.get(clockify_tag_ids[0], "Разработка"),
        )

        key = (time_entry.issue_id, time_entry.rm_activity_name)
        if _ := time_entries.get(key):
            _.hours += time_entry.hours
        else:
            time_entries[key] = time_entry

    # Выводим в консоль результат
    table = [time_entry.get_report_data() for time_entry in time_entries.values()]
    table.sort(key=lambda i: (i[2], i[0]), reverse=True)
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

    # Сохраняем данные в Редмайн
    if not DEBUG_MODE:
        for time_entry in time_entries.values():
            time_entry.push_to_redmine(redmine)
            print("Внимание! Удалите вручную записи в Клокифае!")  # TODO добавить удаление времени из Клокифай
        print(f"Посмотреть затреканное время можно тут: {redmine_url_time_entry}")


if __name__ == "__main__":
    if DEBUG_MODE:
        print("Внимание! В режиме отладки данные из Клокифай не сохранятся в Редмайн!")

    clockify_to_redmine(clockify=ClockifySession(CLOCKIFY_API_KEY), redmine=Redmine(redmine_url, key=REDMINE_API_KEY))
