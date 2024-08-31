QUARTER = "24_3"

# import graph30
COLORS = {
    "Отменена": "#abb2b9",
    "Новая": "#d98880",
    "В работе": "#f0b27a",
    "На проверке и доработке": "#f7dc6f",
    "Ожидает релиз, проверена": "#82e0aa",
    "Выполнена": "#d5d8dc",
    "Ожидание": "#bfc9ca",
    "Ожидание разработки": "#bfc9ca",
}

PRIORITY = {1: "Низкий", 2: "Нормальный", 3: "Высокий", 4: "Срочный", 5: "Немедленный"}

GROUP_MAP = {None: 1, "": 1, "4. План": 5, "3. Критический функционал": 4, "2. Доп. функционал": 3, "1. Доработки": 2}

QUARTER_MAP = {"23_3": 9, "23_4": 8, "24_1": 7, "24_2": 6, "24_3": 5, "24_4": 4, "25_1": 3, "25_2": 2, None: 1, "": 1}
