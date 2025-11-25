from typing import List, Tuple
from ..storage import StorageService


class TipsRepository:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

    # Retorna solo los tips destacados (los primeros 5)
    def featured(self, limit: int = 5) -> List[Tuple]:
        return self.storage.fetchall(
            "SELECT id, title, body, image FROM tips WHERE is_featured = 1 LIMIT ?",
            (limit,),
        )

    # NUEVO: Retorna todos los tips, ordenados por ID
    def list_all(self, limit: int | None = None) -> List[Tuple]:
        query = "SELECT id, title, body, image, category, difficulty, impact, is_featured FROM tips ORDER BY id ASC"
        if limit is not None:
            query += f" LIMIT {limit}"
        return self.storage.fetchall(query)
