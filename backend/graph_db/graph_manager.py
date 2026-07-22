import json
import networkx as nx
from pathlib import Path

GRAPH = nx.MultiDiGraph()

DATA_FILE = Path("data/complaints.json")


def load_complaints():
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_complaint(complaint):

    complaints = load_complaints()

    complaints.append(complaint)

    with open(DATA_FILE, "w") as f:
        json.dump(complaints, f, indent=4)


def build_graph():

    GRAPH.clear()

    complaints = load_complaints()

    for complaint in complaints:

        complaint_id = complaint["id"]

        GRAPH.add_node(
            complaint_id,
            type="complaint"
        )

        entities = complaint["entities"]

        for entity_type, values in entities.items():

            if not isinstance(values, list):
                values = [values]

            for value in values:

                if not value:
                    continue

                node_id = f"{entity_type}:{value}"

                GRAPH.add_node(
                    node_id,
                    type=entity_type,
                    value=value
                )

                GRAPH.add_edge(
                    complaint_id,
                    node_id,
                    relation="contains"
                )

    return GRAPH

def find_related_complaints(entities):

    build_graph()

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