from typing import TYPE_CHECKING, Final, Literal, Optional
from pyvis.network import Network
from graph30.constants import OPTIONS
import networkx as nx

import psycopg2
from config import DATABASE_URI_REPORTS_REDMINE
from graph30.models import RedmineTask

connect = psycopg2.connect(DATABASE_URI_REPORTS_REDMINE)

if TYPE_CHECKING:
    from networkx import DiGraph
    from graph30 import typing


def get_musthave_crm_task_ids(filter: "typing.FilterType", quarter: Optional[str] = None) -> set[int]:
    result = []
    cursor = connect.cursor()

    if filter == "all":
        cursor.execute(
            """
            SELECT
                i.id
            FROM
                issues i
            WHERE
                i.project_id = 69
            """
        )
        result = cursor.fetchall()

    elif filter == "opened":
        cursor.execute(
            """
            SELECT
                i.id
            FROM
                issues i
            WHERE
                i.project_id = 69
                AND i.tracker_id != 6
                AND i.status_id NOT IN (5, 10)
            """
        )
        result = cursor.fetchall()

    elif filter == "quarter" and quarter:
        cursor.execute(
            f"""
            SELECT
                i.id
            FROM
                issues i
                LEFT JOIN custom_values cv22 ON cv22.customized_id = i.id
            WHERE
                i.project_id = 69
                AND i.tracker_id != 6
                AND i.status_id NOT IN (5, 10)
                AND cv22.custom_field_id = 22
                AND cv22.value = '{quarter}'
            """
        )
        result = cursor.fetchall()

    elif filter == "quarter_plan" and quarter:
        cursor.execute(
            f"""
            SELECT
                i.id,
                cv22.value,
                cv21.value
            FROM
                issues i
                LEFT JOIN custom_values cv21 ON cv21.customized_id = i.id
                LEFT JOIN custom_values cv22 ON cv22.customized_id = i.id
            WHERE
                i.project_id = 69
                AND i.tracker_id != 6
                AND i.status_id NOT IN (5, 10)
                AND cv22.custom_field_id = 22
                AND cv22.value = '{quarter}'
                AND cv21.custom_field_id = 21
                AND cv21.value = '3. Важно и не срочно'
            """
        )
        result = cursor.fetchall()

    elif filter == "custom":
        cursor.execute(
            """
            SELECT
                i.id
            FROM
                issues i
                LEFT JOIN custom_values cv25 ON cv25.customized_id = i.id
            WHERE
                i.project_id = 69
                AND i.tracker_id != 6
                AND i.status_id NOT IN (5, 10)
                AND cv25.custom_field_id = 25
                AND cv25.value = '1'
            """
        )
        result = cursor.fetchall()

    else:
        raise Exception("Cant execute sql. Check if/else-blocks")

    return set(row[0] for row in result)


def get_task_blocked_links(task_ids: set[int]) -> list[tuple[int, int]]:
    cursor = connect.cursor()

    cursor.execute(
        f"""
        SELECT
            ir.issue_from_id,
            ir.issue_to_id
        FROM
            issue_relations ir
        WHERE
            ir.relation_type = 'blocks'
            AND (
                ir.issue_from_id IN {str(tuple(task_ids)).replace(",)", ")")}
                OR ir.issue_to_id IN {str(tuple(task_ids)).replace(",)", ")")}
            )
        """
    )

    return cursor.fetchall()


def get_redmine_tasks(task_ids: set) -> dict[int, "RedmineTask"]:
    cursor = connect.cursor()
    cursor.execute(
        f"""
        SELECT
            i.id,
            i.estimated_hours,
            tr."name" tracker_name,
            istat."name" status_name,
            u.lastname lastname,
            i.created_on,
            i.priority_id,
            i.subject,
            cv21.value,
            cv22.value,
            i.project_id,
            cv25.value
        FROM
            issues i
            JOIN trackers tr ON tr.id = i.tracker_id
            JOIN issue_statuses istat ON istat.id = i.status_id

            LEFT JOIN users u ON u.id = i.assigned_to_id
            LEFT JOIN custom_values cv21 on cv21.customized_id = i.id and cv21.custom_field_id = 21
            LEFT JOIN custom_values cv22 on cv22.customized_id = i.id and cv22.custom_field_id = 22
            LEFT JOIN custom_values cv25 on cv25.customized_id = i.id and cv25.custom_field_id = 25
        WHERE
            i.id IN {str(tuple(task_ids)).replace(",)", ")")}
        """
    )

    result = dict()
    for row in cursor.fetchall():
        kpi = True if row[11] == "1" else False
        result[row[0]] = RedmineTask(
            id=row[0],
            subject=row[7],
            estimated_hours=row[1],
            responsible_lastname=row[4],
            kpi=kpi,
            quarter=row[9],
            group=row[8],
            priority_id=row[6],
            tracker=row[2],
            status=row[3],
            d_create=row[5],
            project_id=row[10],
        )

    return result


def render_graph(G: "DiGraph"):
    net = Network()
    net.from_nx(G)
    # net.show_buttons(filter_=["edges", "layout", "physics"])
    net.set_options(OPTIONS)

    net.show("graph30.html", notebook=False)  # save visualization in 'graph.html'
    return


def find_roots(G: "DiGraph") -> set[int]:
    nodes: set[int] = set()
    neighbours: set[int] = set()
    for node, data in G.adjacency():
        nodes.add(node)
        neighbours.update(data.keys())
    return set(nodes - neighbours)


def find_roots_and_leaves(G: "DiGraph") -> tuple[set[int], set[int]]:
    roots = set()
    leaves = set()
    for node in G.nodes:
        successors = list(G.successors(node))
        predecessors = list(G.predecessors(node))

        if not predecessors:
            roots.add(node)
        elif predecessors and not successors:
            leaves.add(node)
    return roots, leaves


def cascade_tasks_blocks(task_ids: set, layers: "typing.LayersType"):
    step = 0
    links = []

    while step < layers:
        step += 1
        links = get_task_blocked_links(task_ids)
        for from_id, to_id in links:
            task_ids.update((from_id, to_id))

    return task_ids, links


def get_roots(G: "DiGraph") -> set[int]:
    return set(v for v, d in G.in_degree() if d == 0)


def get_leaves(G: "DiGraph") -> set[int]:
    return set(v for v, d in G.out_degree() if d == 0)


def get_incorrect_links(G: "DiGraph") -> list[dict[Literal["incorect", "corect"], tuple[int, ...]]]:
    result = []
    nodes_without_roots = set(G.nodes) - get_roots(G)
    for node in G.nodes:
        paths = tuple(nx.all_simple_paths(G, source=node, target=nodes_without_roots, cutoff=2))
        path2 = tuple(tuple(path) for path in paths if len(path) == 2)
        path3 = tuple(tuple(path) for path in paths if len(path) == 3)

        for start, _, end in path3:
            if (start, end) in path2:
                result.append({"correct": (start, end), "incorect": (start, _, end)})
    return result


def get_incorrect_priority(G: "DiGraph", tasks: dict[int, "RedmineTask"]):
    STATUSES: Final[tuple[Literal["Выполнена"], Literal["Отменена"]]] = ("Выполнена", "Отменена")
    result = set()
    nodes_without_roots = set(G.nodes) - get_roots(G)
    for node in G.nodes:
        paths = tuple(nx.all_simple_paths(G, source=node, target=nodes_without_roots, cutoff=2))

        for path in paths:
            pre_task = None
            post_task = None
            pre_code = 9999

            for elem in path:
                post_task = tasks.get(elem)
                if not post_task:
                    continue
                post_code = post_task.code
                if pre_code < post_code and pre_task and pre_task.status not in STATUSES:
                    result.add((pre_task.id, post_task.id))
                pre_task = post_task
                pre_code = post_code
    return result


def get_solo_nodes(G: "DiGraph") -> tuple[int]:
    out = set(G.out_degree())
    in_ = set(G.in_degree())
    _ = out & in_
    return tuple(node for node, count in _ if count == 0)


def remove_solo_nodes(G: "DiGraph") -> tuple[int]:
    remove_nodes = get_solo_nodes(G)
    G.remove_nodes_from(remove_nodes)
    return remove_nodes


def delete_incorrect_links(connect, incorrect_links):
    connect.execute(
        """
        SELECT id FROM issue_relations
        WHERE
            (issue_from_id = 26761 and issue_to_id = 26820)
            or (issue_from_id = 26761 and issue_to_id = 26807)
            or (issue_from_id = 26761 and issue_to_id = 26808)
            or (issue_from_id = 26761 and issue_to_id = 27036)
            or (issue_from_id = 26761 and issue_to_id = 27133)
            or (issue_from_id = 26761 and issue_to_id = 26799)
            or (issue_from_id = 26761 and issue_to_id = 26808)
            or (issue_from_id = 26761 and issue_to_id = 27035)
            or (issue_from_id = 26761 and issue_to_id = 27036)
            or (issue_from_id = 26761 and issue_to_id = 27133)
            or (issue_from_id = 26761 and issue_to_id = 27133)
            or (issue_from_id = 26761 and issue_to_id = 27133)
            or (issue_from_id = 26764 and issue_to_id = 27133)
            or (issue_from_id = 26764 and issue_to_id = 27133)
            or (issue_from_id = 26805 and issue_to_id = 26807)
            or (issue_from_id = 26805 and issue_to_id = 26808)
            or (issue_from_id = 26805 and issue_to_id = 26818)
            or (issue_from_id = 26805 and issue_to_id = 27036)
            or (issue_from_id = 26805 and issue_to_id = 27133)
            or (issue_from_id = 26805 and issue_to_id = 26799)
            or (issue_from_id = 26805 and issue_to_id = 26808)
            or (issue_from_id = 26805 and issue_to_id = 27036)
            or (issue_from_id = 26805 and issue_to_id = 27133)
            or (issue_from_id = 26805 and issue_to_id = 26836)
            or (issue_from_id = 26805 and issue_to_id = 27133)
            or (issue_from_id = 26806 and issue_to_id = 27133)
            and relation_type = 'blocks'
        """
    )
