import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


def _database_path() -> Path:
    configured = os.getenv("ADVISORY_DATABASE_PATH", "data/advisory.sqlite3")
    path = Path(configured)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(_database_path(), timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS farmer_profiles (
                farmer_id TEXT PRIMARY KEY,
                location TEXT NOT NULL DEFAULT '',
                crops_grown TEXT NOT NULL DEFAULT '',
                soil_type TEXT NOT NULL DEFAULT '',
                land_size TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS advisory_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                original_input TEXT NOT NULL,
                input_type TEXT NOT NULL,
                intent TEXT NOT NULL,
                retrieved_sources TEXT NOT NULL,
                advisory TEXT NOT NULL,
                language TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_advisory_farmer_created
                ON advisory_interactions(farmer_id, id DESC);
            """
        )


def get_profile(farmer_id: str) -> dict[str, str]:
    with _connect() as connection:
        row = connection.execute(
            "SELECT farmer_id, location, crops_grown, soil_type, land_size "
            "FROM farmer_profiles WHERE farmer_id = ?",
            (farmer_id,),
        ).fetchone()
    if row is None:
        return {
            "farmer_id": farmer_id,
            "location": "",
            "crops_grown": "",
            "soil_type": "",
            "land_size": "",
        }
    return dict(row)


def save_profile(farmer_id: str, profile: dict[str, str]) -> dict[str, str]:
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO farmer_profiles (farmer_id, location, crops_grown, soil_type, land_size)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(farmer_id) DO UPDATE SET
                location = excluded.location,
                crops_grown = excluded.crops_grown,
                soil_type = excluded.soil_type,
                land_size = excluded.land_size,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                farmer_id,
                profile.get("location", ""),
                profile.get("crops_grown", ""),
                profile.get("soil_type", ""),
                profile.get("land_size", ""),
            ),
        )
    return get_profile(farmer_id)


def add_interaction(interaction: dict[str, Any]) -> dict[str, Any]:
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO advisory_interactions
                (farmer_id, original_input, input_type, intent, retrieved_sources, advisory, language)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                interaction["farmer_id"],
                interaction["original_input"],
                interaction["input_type"],
                interaction["intent"],
                json.dumps(interaction["retrieved_sources"], ensure_ascii=False),
                interaction["advisory"],
                interaction["language"],
            ),
        )
        row = connection.execute(
            "SELECT * FROM advisory_interactions WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return _decode_interaction(row)


def get_history(farmer_id: str, limit: int = 20) -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT * FROM advisory_interactions WHERE farmer_id = ? "
            "ORDER BY id DESC LIMIT ?",
            (farmer_id, limit),
        ).fetchall()
    return [_decode_interaction(row) for row in rows]


def get_recent_context(farmer_id: str, limit: int = 5) -> list[dict[str, str]]:
    return [
        {"query": item["original_input"], "advisory": item["advisory"]}
        for item in get_history(farmer_id, limit)
    ]


def _decode_interaction(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    result["retrieved_sources"] = json.loads(result["retrieved_sources"])
    return result
