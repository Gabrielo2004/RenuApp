import os
import sqlite3
from pathlib import Path
from typing import Optional


class StorageService:
    """Thin wrapper around SQLite with schema initialization.

    This service is intentionally simple for the MVP. It enables local
    persistence to satisfy project requirements and provides a foundation for
    future repositories.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            # Default database path inside the app directory
            base_dir = Path(__file__).resolve().parent.parent
            db_path = str(base_dir / "renu.db")

        self.db_path = str(Path(db_path))

    def get_connection(self) -> sqlite3.Connection:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_database(self) -> None:
        with self.get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS recycling_points (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    address TEXT,
                    lat REAL NOT NULL,
                    lon REAL NOT NULL,
                    hours TEXT,
                    is_open INTEGER DEFAULT 1,
                    notes TEXT
                );

                CREATE TABLE IF NOT EXISTS materials (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS point_materials (
                    point_id INTEGER NOT NULL,
                    material_id INTEGER NOT NULL,
                    PRIMARY KEY (point_id, material_id),
                    FOREIGN KEY (point_id) REFERENCES recycling_points(id) ON DELETE CASCADE,
                    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS tips (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    body TEXT,
                    image TEXT,
                    category TEXT,
                    difficulty TEXT,
                    impact TEXT,
                    is_featured INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS challenges (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    period TEXT NOT NULL,          -- 'daily'|'weekly'|'once'
                    target INTEGER NOT NULL,
                    unit TEXT NOT NULL,            -- e.g., 'items'
                    points_reward INTEGER DEFAULT 0,
                    is_weekly INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS challenge_progress (
                    challenge_id INTEGER PRIMARY KEY,
                    progress INTEGER NOT NULL DEFAULT 0,
                    last_updated TEXT,
                    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS favorites (
                    type TEXT NOT NULL,            -- 'point'|'tip'
                    ref_id INTEGER NOT NULL,
                    PRIMARY KEY (type, ref_id)
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
                """
            )
            conn.commit()

    # --- simple helpers ---
    def fetchone(self, query: str, params: tuple = ()):
        with self.get_connection() as conn:
            cur = conn.execute(query, params)
            return cur.fetchone()

    def fetchall(self, query: str, params: tuple = ()):  # list of rows
        with self.get_connection() as conn:
            cur = conn.execute(query, params)
            return cur.fetchall()

    def execute(self, query: str, params: tuple = ()) -> None:
        with self.get_connection() as conn:
            conn.execute(query, params)
            conn.commit()


