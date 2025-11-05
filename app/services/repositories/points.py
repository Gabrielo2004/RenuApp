from typing import List, Dict, Optional, Iterable

from ..storage import StorageService


class PointsRepository:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

    def list_points(self, material_filters: Optional[Iterable[str]] = None) -> List[Dict]:
        rows = self.storage.fetchall(
            """
            SELECT rp.id, rp.name, rp.address, rp.lat, rp.lon, rp.hours,
                   GROUP_CONCAT(m.name, '|') as mats
            FROM recycling_points rp
            LEFT JOIN point_materials pm ON pm.point_id = rp.id
            LEFT JOIN materials m ON m.id = pm.material_id
            GROUP BY rp.id
            ORDER BY rp.id ASC
            """
        )
        points: List[Dict] = []
        for r in rows:
            (_id, name, address, lat, lon, hours, mats) = r
            materials = [x for x in (mats.split('|') if mats else []) if x]
            points.append({
                "id": int(_id),
                "name": name or "",
                "address": address or "",
                "lat": float(lat),
                "lon": float(lon),
                "hours": hours or "",
                "materials": materials,
            })
        if material_filters:
            filt = set(material_filters)
            points = [p for p in points if any(m in filt for m in p.get("materials", []))]
        return points

    def list_materials(self) -> List[str]:
        rows = self.storage.fetchall("SELECT name FROM materials ORDER BY name ASC")
        return [r[0] for r in rows if r and r[0]]
