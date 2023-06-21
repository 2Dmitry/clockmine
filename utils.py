from typing import TYPE_CHECKING

from constants import coefficient

if TYPE_CHECKING:
    from clockify.session import ClockifySession


def get_clockify_tags_map(clockify: "ClockifySession", clockify_workspace_id: str) -> dict[str, str]:
    """Вернет словарь, где ключ - это строка в формате '648f1d8cabc41f2c318b5768', значение - 'Разработка'"""
    return {tag.id_: tag.name for tag in clockify.tag.get_tags(clockify_workspace_id)}


def secs_to_hours(secs: float) -> float:
    return round(secs / 60 / 60 * coefficient, 2)
