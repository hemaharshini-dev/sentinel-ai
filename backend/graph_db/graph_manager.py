import json
import threading
import networkx as nx
from pathlib import Path

GRAPH = nx.MultiDiGraph()

DATA_FILE = Path("data/complaints.json")

_graph_dirty = True       # rebuild on first use and after every save
_graph_lock = threading.Lock()  # prevent concurrent rebuilds


def load_complaints():
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_complaint(complaint):
    global _graph_dirty

    complaints = load_complaints()

    # Remove any existing entry with the same ID before appending
    complaints = [c for c in complaints if c["id"] != complaint["id"]]

    complaints.append(complaint)

    with open(DATA_FILE, "w") as f:
        json.dump(complaints, f, indent=4)

    # Mark graph as stale so the next query triggers a rebuild
    _graph_dirty = True


def build_graph():

    GRAPH.clear()

    complaints = load_complaints()

    for complaint in complaints:

        complaint_id = complaint["id"]

        GRAPH.add_node(complaint_id, type="complaint")

        entities = complaint["entities"]

        for entity_type, values in entities.items():

            if not isinstance(values, list):
                values = [values]

            for value in values:

                if not value:
                    continue

                node_id = f"{entity_type}:{value}"

                GRAPH.add_node(node_id, type=entity_type, value=value)

                GRAPH.add_edge(complaint_id, node_id, relation="contains")

    return GRAPH


def find_related_complaints(entities):
    global _graph_dirty

    # Only rebuild when new data has been written; lock to avoid race conditions
    with _graph_lock:
        if _graph_dirty:
            build_graph()
            _graph_dirty = False

    related = {}

    for entity_type, values in entities.items():

        if not isinstance(values, list):
            values = [values]

        for value in values:

            if not value:
                continue

            node = f"{entity_type}:{value}"

            if node not in GRAPH:
                continue

            for complaint in GRAPH.predecessors(node):

                if complaint not in related:
                    related[complaint] = []

                related[complaint].append(
                    {
                        "entity_type": entity_type,
                        "value": value,
                    }
                )

    return related
