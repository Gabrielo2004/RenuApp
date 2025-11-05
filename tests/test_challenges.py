def test_weekly_challenge_and_progress(challenges_repo):
    weekly = challenges_repo.get_weekly()
    if weekly is None:
        # Seed a minimal weekly challenge if not present (assets images may be missing)
        storage = challenges_repo.storage
        storage.execute(
            """
            INSERT INTO challenges(id, title, description, period, target, unit, points_reward, is_weekly)
            VALUES (1, 'Desafío Semanal', 'Progreso semanal', 'weekly', 5, 'items', 50, 1)
            """
        )
        storage.execute("INSERT INTO challenge_progress(challenge_id, progress) VALUES (1, 0)")
        weekly = challenges_repo.get_weekly()

    assert weekly is not None
    cid = int(weekly[0])

    before = challenges_repo.get_progress(cid)
    challenges_repo.ensure_progress_row(cid)
    after = challenges_repo.increment_progress(cid, 2)
    assert after == before + 2


