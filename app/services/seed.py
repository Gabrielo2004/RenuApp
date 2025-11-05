from .storage import StorageService
from pathlib import Path
from typing import List


def seed_if_empty(storage: StorageService) -> None:
    # Materials
    row = storage.fetchone("SELECT COUNT(*) FROM materials")
    if not row or row[0] == 0:
        for name in ("Papel", "Plástico", "Vidrio"):
            storage.execute("INSERT INTO materials(name) VALUES (?)", (name,))

    # Tips
    row = storage.fetchone("SELECT COUNT(*) FROM tips")
    count = row[0] if row else 0
    if count == 0:
        initial = [
            ("Separa por material", "Clasifica papel, plástico y vidrio para facilitar el reciclaje.", "assets/images/tip1.jpg", "Básico", "Fácil", "Alto" , 1),
            ("Limpia envases", "Enjuaga los envases para evitar contaminación.", "assets/images/tip2.jpg", "Básico", "Fácil", "Medio" , 1),
            ("Compra a granel", "Reduce envases eligiendo compras a granel.", "assets/images/tip3.jpg", "Avanzado", "Media", "Alto", 0),
            ("Usa botellas reutilizables", "Evita botellas desechables y rellena una reutilizable.", "assets/images/tip4.jpg", "Básico", "Fácil", "Medio", 0),
            ("Bolsa de tela", "Lleva tu bolsa reutilizable cuando compres.", "assets/images/tip5.jpg", "Básico", "Fácil", "Medio", 0),
        ]
        for t in initial:
            storage.execute(
                """
                INSERT INTO tips(title, body, image, category, difficulty, impact, is_featured)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                t,
            )
    elif count < 5:
        extra = [
            ("Usa botellas reutilizables", "Evita botellas desechables y rellena una reutilizable.", "assets/images/tip4.jpg", "Básico", "Fácil", "Medio", 0),
            ("Bolsa de tela", "Lleva tu bolsa reutilizable cuando compres.", "assets/images/tip5.jpg", "Básico", "Fácil", "Medio", 0),
        ]
        for t in extra[: 5 - count]:
            storage.execute(
                """
                INSERT INTO tips(title, body, image, category, difficulty, impact, is_featured)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                t,
            )


def _list_asset_images() -> List[str]:
    base = Path("assets/images")
    if not base.exists():
        return []
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    files = [str(p.as_posix()) for p in sorted(base.iterdir()) if p.suffix.lower() in exts]
    return files[:5]


def sync_tip_images(storage: StorageService) -> None:
    """Sync tips.image fields with files inside assets/images (up to 5).

    - Updates existing tips in order with the found image paths.
    - Inserts new tips if there are more images than existing tips (with generic content).
    - Ensures first five are marked featured.
    """
    images = _list_asset_images()
    if not images:
        return

    rows = storage.fetchall("SELECT id FROM tips ORDER BY id ASC")
    # Update existing rows
    for idx, img in enumerate(images[: len(rows)]):
        storage.execute(
            "UPDATE tips SET image = ?, is_featured = ? WHERE id = ?",
            (img, 1 if idx < 5 else 0, rows[idx][0]),
        )
    # Insert if needed
    if len(images) > len(rows):
        for idx, img in enumerate(images[len(rows) :]):
            storage.execute(
                """
                INSERT INTO tips(title, body, image, category, difficulty, impact, is_featured)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Consejo Eco",
                    "Práctica sustentable para tu día a día.",
                    img,
                    "General",
                    "Fácil",
                    "Medio",
                    1 if (len(rows) + idx) < 5 else 0,
                ),
            )

    # Challenges
    row = storage.fetchone("SELECT COUNT(*) FROM challenges")
    if not row or row[0] == 0:
        storage.execute(
            """
            INSERT INTO challenges(id, title, description, period, target, unit, points_reward, is_weekly)
            VALUES (1, 'Desafío Semanal', 'Recicla envases durante la semana', 'weekly', 5, 'items', 50, 1)
            """
        )
        storage.execute(
            "INSERT INTO challenge_progress(challenge_id, progress) VALUES (1, 0)"
        )
    # If there are few challenges, add some daily ones for the list
    row = storage.fetchone("SELECT COUNT(*) FROM challenges")
    count_ch = row[0] if row else 0
    if count_ch < 3:
        extras = [
            ("Evita bolsas plásticas por 3 días", "Usa bolsa reutilizable", "daily", 3, "days", 10, 0),
            ("Separa tu basura orgánica 4 días", "Hábito diario de separación", "daily", 4, "days", 15, 0),
        ]
        for (title, desc, period, target, unit, points, is_weekly) in extras[: max(0, 3 - count_ch)]:
            storage.execute(
                "INSERT INTO challenges(title, description, period, target, unit, points_reward, is_weekly) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title, desc, period, target, unit, points, is_weekly),
            )

    # Recycling points & relations (seed minimal if empty)
    row = storage.fetchone("SELECT COUNT(*) FROM recycling_points")
    if not row or row[0] == 0:
        # Ensure materials that appear in examples exist
        for m in ("Cartón", "Latas"):
            storage.execute("INSERT OR IGNORE INTO materials(name) VALUES (?)", (m,))

        examples = [
            {
                "name": "Universidad de La Frontera",
                "address": "Av. Francisco Salazar 01145",
                "lat": -38.739,
                "lon": -72.598,
                "hours": "24 horas",
                "materials": ("Papel", "Plástico", "Vidrio"),
            },
            {
                "name": "Plaza Aníbal Pinto",
                "address": "Plaza Aníbal Pinto",
                "lat": -38.735,
                "lon": -72.590,
                "hours": "6:00 - 22:00",
                "materials": ("Papel", "Cartón"),
            },
            {
                "name": "Mall Temuco",
                "address": "Av. Alemania 067",
                "lat": -38.741,
                "lon": -72.612,
                "hours": "10:00 - 22:00",
                "materials": ("Plástico", "Vidrio", "Latas"),
            },
        ]

        for ex in examples:
            storage.execute(
                "INSERT INTO recycling_points(name, address, lat, lon, hours, is_open, notes) VALUES (?, ?, ?, ?, ?, 1, NULL)",
                (ex["name"], ex["address"], ex["lat"], ex["lon"], ex["hours"]),
            )
            # Get last inserted id
            row_id = storage.fetchone("SELECT id FROM recycling_points WHERE name = ? ORDER BY id DESC LIMIT 1", (ex["name"],))
            if not row_id:
                continue
            pid = int(row_id[0])
            for m in ex["materials"]:
                mid = storage.fetchone("SELECT id FROM materials WHERE name = ?", (m,))
                if mid:
                    storage.execute(
                        "INSERT OR IGNORE INTO point_materials(point_id, material_id) VALUES (?, ?)",
                        (pid, int(mid[0])),
                    )


