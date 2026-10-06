from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .constants import APP_VERSION, SCHEMA_VERSION


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateDatabase:
    """SQLite persistence for the V3 compatibility state.

    The current V3 compatibility layer stores the complete validated application
    snapshot in SQLite. This preserves the established business model while keeping
    persistence outside browser storage. Domain tables can be normalized incrementally
    in a future minor release when stronger relational querying is required.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=15)
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS app_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    state_json TEXT NOT NULL,
                    schema_version INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            conn.execute(
                "INSERT INTO metadata(key,value) VALUES('schema_version',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(SCHEMA_VERSION),),
            )

    @staticmethod
    def validate_state(raw: str) -> dict[str, Any]:
        state = json.loads(raw)
        if not isinstance(state, dict):
            raise ValueError("El estado debe ser un objeto JSON.")
        for key in ("settings", "clients", "units", "cases"):
            if key not in state:
                raise ValueError(f"Falta el bloque requerido: {key}")
        if not isinstance(state.get("settings"), dict):
            raise ValueError("settings debe ser un objeto.")
        for key in ("clients", "units", "cases"):
            if not isinstance(state.get(key), list):
                raise ValueError(f"{key} debe ser una lista.")
        meta = state.setdefault("meta", {})
        if not isinstance(meta, dict):
            meta = state["meta"] = {}
        meta["schemaVersion"] = SCHEMA_VERSION
        meta["appVersion"] = APP_VERSION
        return state

    def load(self) -> str | None:
        with self.connect() as conn:
            row = conn.execute("SELECT state_json FROM app_state WHERE id=1").fetchone()
            return row[0] if row else None

    def save(self, raw: str) -> bool:
        state = self.validate_state(raw)
        encoded = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        with self.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "INSERT INTO app_state(id,state_json,schema_version,updated_at) VALUES(1,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET state_json=excluded.state_json, "
                "schema_version=excluded.schema_version, updated_at=excluded.updated_at",
                (encoded, SCHEMA_VERSION, utc_now()),
            )
            conn.commit()
        return True

    def clear(self) -> bool:
        with self.connect() as conn:
            conn.execute("DELETE FROM app_state WHERE id=1")
        return True

    def integrity_check(self) -> str:
        with self.connect() as conn:
            return str(conn.execute("PRAGMA integrity_check").fetchone()[0])

    def backup_to(self, destination: Path) -> Path:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as source, sqlite3.connect(destination) as target:
            source.backup(target)
        return destination
