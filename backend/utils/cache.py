"""
Persistent LLM cache backed by SQLite.
Extends langchain_core.caches.BaseCache using only stdlib — no langchain_community needed.

Caches LLM responses so identical prompts skip the API entirely across server restarts.
"""
import json
import sqlite3
import hashlib
import logging
from pathlib import Path
from typing import Any, Optional, Sequence

from langchain_core.caches import BaseCache
from langchain_core.outputs import Generation

logger = logging.getLogger(__name__)

CACHE_DB = Path(".llm_cache.db")


class SQLitePersistentCache(BaseCache):
    """
    A simple persistent LLM cache using a local SQLite file.
    Survives server restarts. Thread-safe via SQLite WAL mode.
    """

    def __init__(self, db_path: Path = CACHE_DB):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS llm_cache (
                cache_key   TEXT PRIMARY KEY,
                response    TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
        conn.close()
        logger.debug(f"SQLitePersistentCache initialised at {self.db_path}")

    def _make_key(self, prompt: str, llm_string: str) -> str:
        raw = f"{llm_string}::{prompt}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def lookup(self, prompt: str, llm_string: str) -> Optional[list[Generation]]:
        key = self._make_key(prompt, llm_string)
        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            "SELECT response FROM llm_cache WHERE cache_key = ?", (key,)
        ).fetchone()
        conn.close()

        if row:
            logger.debug(f"Cache HIT for key {key[:12]}...")
            data = json.loads(row[0])
            return [Generation(**g) for g in data]

        return None

    def update(self, prompt: str, llm_string: str, return_val: Sequence[Generation]) -> None:
        key = self._make_key(prompt, llm_string)
        serialised = json.dumps([{"text": g.text, "generation_info": g.generation_info} for g in return_val])
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO llm_cache (cache_key, response) VALUES (?, ?)",
            (key, serialised)
        )
        conn.commit()
        conn.close()
        logger.debug(f"Cache STORED for key {key[:12]}...")

    async def alookup(self, prompt: str, llm_string: str) -> Optional[list[Generation]]:
        return self.lookup(prompt, llm_string)

    async def aupdate(self, prompt: str, llm_string: str, return_val: Sequence[Generation]) -> None:
        self.update(prompt, llm_string, return_val)

    def clear(self, **kwargs: Any) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM llm_cache")
        conn.commit()
        conn.close()
        logger.info("LLM cache cleared")
