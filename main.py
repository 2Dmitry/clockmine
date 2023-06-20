from datetime import datetime

import isodate
from clockify.session import ClockifySession
from environs import Env
from redminelib import Redmine
from tabulate import tabulate

environ = Env()
environ.read_env()
CLOCKIFY_API_KEY = environ("CLOCKIFY_API_KEY")
CLOCKIFY_USER_ID = environ("CLOCKIFY_USER_ID")
CLOCKIFY_WORKPLACE_ID = environ("CLOCKIFY_WORKPLACE_ID")
REDMINE_API_KEY = environ("REDMINE_API_KEY")
REDMINE_USER_ID = environ("REDMINE_USER_ID")
REDMINE_ACTIVITIES_MAP = {"Бизнес-анализ": 8, "Разработка": 9, "Code review": 57, "Внутренние консультации": 58}

DEBUG_MODE = True


def main():
    if DEBUG_MODE:
        print("Внимание! В режиме отладки данные из Клокифай не сохранятся в Редмайн!")

    def _secs_to_hours(secs: float) -> float:
        return round(secs / 60 / 60, 2)

    def _get_clockify_tags(clockify: ClockifySession) -> dict:
        """Вернет словарь, где ключ - это строка в формате '648f1d8cabc41f2c318b5768', значение - 'Разработка'"""
        clockify_tags = dict()
        for tag in clockify.tag.get_tags(CLOCKIFY_WORKPLACE_ID):
            clockify_tags[tag.id_] = tag.name
        return clockify_tags

    clockify = ClockifySession(CLOCKIFY_API_KEY)

    # Парсим теги в Клокифае
    CLOCKIFY_TAGS = _get_clockify_tags(clockify)

    # Парсим затреканное в Клокифае время
    time_entries = dict()
    for clk_time_entry in clockify.time_entry.get_time_entries(CLOCKIFY_WORKPLACE_ID, CLOCKIFY_USER_ID):
        time_entry = dict()
        time_entry["issue_id"] = None
        time_entry["description"] = clk_time_entry.description[:60]
        time_entry["hours"] = _secs_to_hours(
            isodate.parse_duration(clk_time_entry.time_interval.duration).total_seconds()
        )
        time_entry["rm_activity_name"] = (
            CLOCKIFY_TAGS.get(tag_ids[0], "Разработка") if (tag_ids := clk_time_entry.tag_ids) else "Разработка"
        )
        time_entry["activity_id"] = REDMINE_ACTIVITIES_MAP[time_entry["rm_activity_name"]]
        time_entry["spent_on"] = datetime.today().date()
        time_entry["user_id"] = REDMINE_USER_ID
        time_entry["comments"] = ""

        for chunk in time_entry["description"].split(" "):
            if "#" in chunk:
                time_entry["issue_id"] = chunk[1:]
                break

        if time_entry["issue_id"]:
            key = (time_entry["issue_id"], time_entry["rm_activity_name"])
            if result := time_entries.get(key):
                result["hours"] += time_entry["hours"]
            else:
                time_entries[key] = time_entry
        else:
            print("НЕ УКАЗАН НОМЕР ЗАДАЧИ: ", time_entry)

    # Выводим в консоль результат
    table = []
    sum_hours = float(0)
    for time_entry in time_entries.values():
        table.append(tuple(time_entry.values()))
        sum_hours += time_entry["hours"]

    table.sort(key=lambda i: (i[2], i[0]), reverse=True)
    print(
        tabulate(
            table,
            headers=(tuple(time_entries.values())[0].keys()),
            tablefmt="rounded_outline",
            numalign="decimal",
            floatfmt=".2f",
            showindex="always",
        )
    )
    print(sum_hours)

    # Создаем на основе распаршенных данных - объекты класса и сохраняем их в редмайн
    redmine = Redmine("https://redmine.sbps.ru/", key=REDMINE_API_KEY)
    for time_entry in time_entries.values():
        rm_time_entry = redmine.time_entry.new()
        for k, v in time_entry.items():
            setattr(rm_time_entry, k, v)

        if not DEBUG_MODE:
            rm_time_entry.save()


main()
