"""
* create venv *
python3 -m ensurepip
python3 -m pip install --upgrade pip
pip install -r requirements.txt
python
import graph30
import networkx as nx
from graph30.utils import get_incorrect_links, get_roots
from graph30 import G
get_incorrect_links(G)
"""

from typing import TYPE_CHECKING
import networkx as nx
from graph30.constants import COLORS
from graph30.models import RedmineTask
from graph30.utils import (
    get_incorrect_priority,
    get_musthave_crm_task_ids,
    cascade_tasks_blocks,
    get_redmine_tasks,
    render_graph,
    remove_solo_nodes,
    get_incorrect_links,
)

if TYPE_CHECKING:
    from graph30.typing import FilterType

NEED_REMOVE_SOLO_NODES = True
FILTER: "FilterType" = "quarter"
LAYERS: int = 8
NEED_INCORRECT_LINKS_ANALYZE: bool = True
NEED_INCORRECT_PRIORITY_ANALYZE: bool = True
G = nx.DiGraph()

musthave_task_ids = get_musthave_crm_task_ids(filter=FILTER)
print(f"{musthave_task_ids=}")
task_ids, blocked_links = cascade_tasks_blocks(task_ids=set(musthave_task_ids), layers=LAYERS)
tasks: dict[int, "RedmineTask"] = get_redmine_tasks(task_ids)
for task in tasks.values():
    G.add_node(
        task.id,
        size=(task.estimated_hours or 20),
        label=f"{task.code}\n{task.quarter} | {task.group} | {task.priority}\n{task.id} {task.tracker}\n{task.status}\n{task.responsible_lastname or '---'}",
        color=COLORS.get(task.status, ""),
    )
G.add_edges_from(blocked_links)

if NEED_REMOVE_SOLO_NODES:
    print("WARNING! Вы удаляете из графа задачи без каких-либо блокировок -> ")
    print(remove_solo_nodes(G))

if NEED_INCORRECT_LINKS_ANALYZE:
    print("INFO! Вы запросили анализ избыточных блокировок -> ")
    print(get_incorrect_links(G))

if NEED_INCORRECT_PRIORITY_ANALYZE:
    print("INFO! Вы запросили анализ неправильных приоритетов -> ")
    print(get_incorrect_priority(G, tasks))

render_graph(G)
