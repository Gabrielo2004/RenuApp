from typing import List, Tuple

from ..storage import StorageService


class TipsRepository:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

    def featured(self, limit: int = 5) -> List[Tuple]:
        return self.storage.fetchall(
            "SELECT id, title, body, image FROM tips WHERE is_featured = 1 LIMIT ?",
            (limit,),
        )


