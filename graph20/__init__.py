"""
* create venv *
$ pip install -r requirements.txt
$ python
*copy and paste code*
"""

from datetime import date, datetime
import psycopg2
from pyvis.network import Network
import networkx as nx

from graph20.constants import COLORS, OPTIONS, PRIORITY

# from config import DATABASE_URI_REPORTS_REDMINE
DATABASE_URI_REPORTS_REDMINE = "postgresql://milov:ger6u36udsdjetyiyufhjdf@redmine.sbps.ru:5436/postgres"

# from .constants import COLORS, OPTIONS

conn = psycopg2.connect(DATABASE_URI_REPORTS_REDMINE)
cur = conn.cursor()

G = nx.DiGraph()  # создаём объект графа
net = Network(height="1200px")
net.from_nx(G)

# cur.execute(open("graph/tasks.sql", "r").read())
# Отбираем все задачи которые нас интересуют
cur.execute(
    """
    SELECT
        i.id
    FROM
        issues i
    WHERE
        i.project_id = 69
        AND i.status_id NOT IN (5, 10)
"""
)
tasks = cur.fetchall()
print("Вы взяли задачи: ", len(tasks))

# Отбираем все связи интересующих задач
s = tuple(task[0] for task in tasks)
cur.execute(
    f"""
    SELECT
        ir.issue_from_id,
        ir.issue_to_id
    FROM
        issue_relations ir
    WHERE
        ir.relation_type = 'blocks'
        AND (
            ir.issue_from_id IN {s}
            OR ir.issue_to_id IN {s}
        )
"""
)
links = cur.fetchall()
print("Кол-во связей: ", len(links))
task_ids = []
for link in links:
    task_ids.extend(link)

cur.execute(
    f"""
    SELECT
        i.id,
        i.estimated_hours,
        tr."name" tracker_name,
        istat."name" status_name,
        u.lastname lastname,
        i.created_on,
        i.priority_id
    FROM
        issues i
        JOIN trackers tr ON tr.id = i.tracker_id
        JOIN issue_statuses istat ON istat.id = i.status_id

        LEFT JOIN users u ON u.id = i.assigned_to_id
    WHERE
        i.id IN {tuple(task_ids)}
"""
)
tasks = cur.fetchall()
print("Расширенный список задач: ", len(tasks))
nodes = []
for task in tasks:
    # Выкидываем некоторые задачи из графа
    if task[3] in ("Выполнена", "Отменена"):
        continue
    nodes.append(task[0])
    net.add_node(
        task[0],
        size=(task[1] or 20),
        label=f"{task[0]}\n{task[2]} {PRIORITY[task[6]]}\n{task[3]}\n{task[4] or '---'}\n{(date.today() - datetime.date(task[5])).days}",
        color=COLORS.get(task[3], ""),
    )

# Строим связи только для нарисованных задач
for link in links:
    if link[0] in nodes and link[1] in nodes:
        net.add_edge(*link)

# net.show_buttons()
net.set_options(OPTIONS)

net.show("graph.html", notebook=False)  # save visualization in 'graph.html'

conn.close()
