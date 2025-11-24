# app/services/repositories/challenges.py — VERSIÓN FINAL CORREGIDA

from typing import Optional, Tuple
from ..storage import StorageService


class ChallengesRepository:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

    def get_weekly(self) -> Optional[Tuple[int, str, str, int, str, int, int]]:
        return self.storage.fetchone(
            """
            SELECT id, title, description, target, unit, points_reward, is_weekly
            FROM challenges
            WHERE is_weekly = 1
            LIMIT 1
            """
        )

    def get_progress(self, challenge_id: int) -> int:
        row = self.storage.fetchone(
            "SELECT progress FROM challenge_progress WHERE challenge_id = ?",
            (challenge_id,),
        )
        return int(row[0]) if row else 0

    def increment_progress(self, challenge_id: int, amount: int = 1) -> int:
        current = self.get_progress(challenge_id)
        new_value = current + amount

        self.storage.execute(
            """
            UPDATE challenge_progress
            SET progress = ?, last_updated = datetime('now')
            WHERE challenge_id = ?
            """,
            (new_value, challenge_id),
        )
        return new_value

    # ✔ CORRECCIÓN — Método necesario para botón "Reiniciar"
    def set_progress(self, challenge_id: int, value: int) -> None:
        self.storage.execute(
            """
            UPDATE challenge_progress
            SET progress = ?, last_updated = datetime('now')
            WHERE challenge_id = ?
            """,
            (value, challenge_id),
        )

    def list_all(self):
        return self.storage.fetchall(
            """
            SELECT id, title, description, period, target, unit,
                   points_reward, is_weekly
            FROM challenges
            ORDER BY id ASC
            """
        )

    def ensure_progress_row(self, challenge_id: int) -> None:
        exists = self.storage.fetchone(
            "SELECT 1 FROM challenge_progress WHERE challenge_id = ?",
            (challenge_id,),
        )
        if not exists:
            self.storage.execute(
                "INSERT INTO challenge_progress(challenge_id, progress) VALUES (?, 0)",
                (challenge_id,),
            )
