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

from typing import TYPE_CHECKING, Literal
import networkx as nx
from graph30.constants import QUARTER
from graph30.models import RedmineTask
from graph30 import utils
from typing import Final

if TYPE_CHECKING:
    from graph30 import typing
    from networkx import DiGraph

FILTER: "typing.FilterType" = "custom"
ADDITIONAL_TASK_IDS: Final[set[int]] = {27166, 28657, 28463, 23299}  # {27166, 28657, 28463, 23299}  # set()
LAYERS: "typing.LayersType" = 1
NEED_INCORRECT_LINKS_ANALYZE: Final[bool] = True
NEED_INCORRECT_PRIORITY_ANALYZE: Final[bool] = True
SHOW_SOLO_TASKS: Final[bool] = True
ALLOW_COST_FOR_NODE_SIZE: Final[bool] = True
MODE: Final[Literal["release", "default", "all"]] = "all"

G: Final["DiGraph"] = nx.DiGraph()

musthave_task_ids = utils.get_musthave_crm_task_ids(filter=FILTER, quarter=QUARTER)
if ADDITIONAL_TASK_IDS:
    musthave_task_ids.update(ADDITIONAL_TASK_IDS)
print(f"{musthave_task_ids=}")

task_ids, blocked_links = utils.cascade_tasks_blocks(task_ids=set(musthave_task_ids), layers=LAYERS)
tasks: dict[int, "RedmineTask"] = utils.get_redmine_tasks(task_ids)
for task in tasks.values():
    G.add_node(
        task.id,
        size=task.node_size if ALLOW_COST_FOR_NODE_SIZE else 50,
        label=task.sign,
        color=task.color_display,
        borderWidth=1,
    )


def mode_default(G, blocked_links):
    for from_, to_ in blocked_links:
        G.add_edge(from_, to_)


def mode_release(G, tasks):
    release_nodes = set()
    for task in tasks.values():
        if task.due_date:
            release_nodes.add(task.due_date)
    release_nodes = list(release_nodes)
    release_nodes.sort()
    for rel_node in release_nodes:
        print(rel_node)
        G.add_node(rel_node.strftime("%d.%m.%Y"))
    release_links = [(node, release_nodes[i + 1]) for i, node in enumerate(release_nodes[:-1], 0)]
    print(release_links)
    for from_, to_ in release_links:
        G.add_edge(from_.strftime("%d.%m.%Y"), to_.strftime("%d.%m.%Y"))

    for task in tasks.values():
        if task.due_date:
            G.add_edge(task.id, task.due_date.strftime("%d.%m.%Y"))


if MODE == "release":
    # RELEASE plan
    mode_release(G, tasks)

elif MODE == "default":
    mode_default(G, blocked_links)

elif MODE == "all":
    mode_release(G, tasks)
    mode_default(G, blocked_links)


if not SHOW_SOLO_TASKS:
    print(f"WARNING! Вы удаляете из графа задачи без каких-либо блокировок -> {utils.remove_solo_nodes(G)}")

if NEED_INCORRECT_LINKS_ANALYZE:
    print(f"INFO! Вы запросили анализ избыточных блокировок -> {utils.get_incorrect_links(G)}")

if NEED_INCORRECT_PRIORITY_ANALYZE:
    print(f"INFO! Вы запросили анализ неправильных приоритетов -> {utils.get_incorrect_priority(G, tasks)}")

utils.render_graph(G)
