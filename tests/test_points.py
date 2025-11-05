def test_list_points_and_filter(points_repo):
    all_points = points_repo.list_points()
    assert isinstance(all_points, list)
    if len(all_points) == 0:
        # Seed minimal point + material relation
        storage = points_repo.storage
        storage.execute("INSERT OR IGNORE INTO materials(name) VALUES ('Papel')")
        storage.execute(
            "INSERT INTO recycling_points(name, address, lat, lon, hours, is_open, notes) VALUES (?, ?, ?, ?, ?, 1, NULL)",
            ("Punto A", "Calle Falsa 123", -38.7, -72.6, "24h"),
        )
        pid_row = storage.fetchone("SELECT id FROM recycling_points WHERE name = ? ORDER BY id DESC LIMIT 1", ("Punto A",))
        mid_row = storage.fetchone("SELECT id FROM materials WHERE name = 'Papel'")
        if pid_row and mid_row:
            storage.execute(
                "INSERT OR IGNORE INTO point_materials(point_id, material_id) VALUES (?, ?)",
                (int(pid_row[0]), int(mid_row[0])),
            )
        all_points = points_repo.list_points()
    assert len(all_points) >= 1

    # Derive a material filter from existing data
    mats = set()
    for p in all_points:
        for m in p.get("materials", []):
            mats.add(m)
    if mats:
        some_filter = [next(iter(mats))]
        filtered = points_repo.list_points(material_filters=some_filter)
        for p in filtered:
            assert any(m in some_filter for m in p.get("materials", []))


