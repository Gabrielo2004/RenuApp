import pytest

from app.services.storage import StorageService
from app.services.repositories.users import UserRepository
from app.services.repositories.challenges import ChallengesRepository
from app.services.repositories.points import PointsRepository
from app.services.repositories.tips import TipsRepository
from app.services.seed import seed_if_empty


@pytest.fixture
def tmp_storage(tmp_path):
    db_file = tmp_path / "test.db"
    storage = StorageService(db_path=str(db_file))
    storage.initialize_database()
    return storage


@pytest.fixture
def user_repo(tmp_storage):
    return UserRepository(tmp_storage)


@pytest.fixture
def challenges_repo(tmp_storage):
    # Seed minimal data to ensure challenges exist
    seed_if_empty(tmp_storage)
    return ChallengesRepository(tmp_storage)


@pytest.fixture
def points_repo(tmp_storage):
    # Seed minimal data to ensure points and materials exist
    seed_if_empty(tmp_storage)
    return PointsRepository(tmp_storage)


@pytest.fixture
def tips_repo(tmp_storage):
    seed_if_empty(tmp_storage)
    return TipsRepository(tmp_storage)


