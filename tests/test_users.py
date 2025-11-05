import pytest


def test_create_and_authenticate_user(user_repo):
    uid = user_repo.create_user("testuser", "secret123", "t@t.com")
    assert uid > 0
    assert user_repo.authenticate("testuser", "secret123") == uid
    assert user_repo.authenticate("testuser", "wrong") is None
    assert user_repo.authenticate("nope", "secret123") is None


def test_duplicate_user_raises(user_repo):
    user_repo.create_user("dup", "pass123", None)
    with pytest.raises(ValueError):
        user_repo.create_user("dup", "pass123", None)


def test_session_set_get_clear(user_repo):
    user_repo.set_current_user_id(42)
    assert user_repo.get_current_user_id() == 42
    user_repo.clear_session()
    assert user_repo.get_current_user_id() is None


