import json
import logging
import sqlite3
import threading
import networkx as nx
from pathlib import Path

logger = logging.getLogger(__name__)

GRAPH = nx.MultiDiGraph()

DB_FILE = Path("data/complaints.db")

_graph_dirty = True
_graph_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

def init_db():
    """Create the complaints table if it doesn't exist."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id          TEXT PRIMARY KEY,
            created_at  TEXT,
            scam_type   TEXT,
            raw_message TEXT,
            entities    TEXT
        )
    """)
    conn.commit()
    conn.close()


# Initialise on import
init_db()


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def save_complaint(complaint: dict):
    global _graph_dirty

    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """
        INSERT INTO complaints (id, created_at, scam_type, raw_message, entities)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            created_at  = excluded.created_at,
            scam_type   = excluded.scam_type,
            raw_message = excluded.raw_message,
            entities    = excluded.entities
        """,
        (
            complaint["id"],
            complaint.get("created_at", ""),
            complaint.get("scam_type", "unknown"),
            complaint.get("raw_message", ""),
            json.dumps(complaint.get("entities", {})),
        ),
    )
    conn.commit()
    conn.close()

    _graph_dirty = True
    logger.info(f"Saved complaint {complaint['id']} to SQLite")


def load_complaints() -> list:
    """Return all complaints as a list of dicts (same shape as before)."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, created_at, scam_type, raw_message, entities FROM complaints ORDER BY created_at ASC"
    ).fetchall()
    conn.close()

    complaints = []
    for row in rows:
        complaints.append({
            "id":          row["id"],
            "created_at":  row["created_at"],
            "scam_type":   row["scam_type"],
            "raw_message": row["raw_message"],
            "entities":    json.loads(row["entities"]),
        })
    return complaints


def get_complaint(complaint_id: str) -> dict | None:
    """Fetch a single complaint by ID."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT id, created_at, scam_type, raw_message, entities FROM complaints WHERE id = ?",
        (complaint_id,)
    ).fetchone()
    conn.close()

    if not row:
        return None
    return {
        "id":          row["id"],
        "created_at":  row["created_at"],
        "scam_type":   row["scam_type"],
        "raw_message": row["raw_message"],
        "entities":    json.loads(row["entities"]),
    }


def get_stats() -> dict:
    """Return complaint counts grouped by scam type."""
    conn = sqlite3.connect(DB_FILE)
    total = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    rows = conn.execute(
        "SELECT scam_type, COUNT(*) as count FROM complaints GROUP BY scam_type ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return {
        "total_complaints": total,
        "by_scam_type": [{"type": r[0], "count": r[1]} for r in rows],
    }


def list_complaints_paged(page: int = 1, limit: int = 20) -> list:
    """Return a paginated list of complaints (id, created_at, scam_type only)."""
    offset = (page - 1) * limit
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute(
        "SELECT id, created_at, scam_type FROM complaints ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    conn.close()
    return [{"id": r[0], "created_at": r[1], "scam_type": r[2]} for r in rows]


# ---------------------------------------------------------------------------
# NetworkX graph for entity matching
# ---------------------------------------------------------------------------

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


def find_related_complaints(entities: dict) -> dict:
    global _graph_dirty

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
                related[complaint].append({
                    "entity_type": entity_type,
                    "value": value,
                })

    return related
