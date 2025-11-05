from types import SimpleNamespace
import pytest

try:
    from app.screens.auth import LoginScreen, RegisterScreen
    from app.services.repositories.users import UserRepository
    from app.services.storage import StorageService
except ModuleNotFoundError:
    pytest.skip("KivyMD no instalado; se omiten pruebas de UI", allow_module_level=True)


class _Text:
    def __init__(self, text=""):
        self.text = text


class FakeApp:
    def __init__(self, users_repo: UserRepository):
        self.users_repo = users_repo
        self.logged = False
        self.switched_to = None

    def set_logged_in(self, v: bool):
        self.logged = v

    def switch_to(self, name: str):
        self.switched_to = name


@pytest.fixture
def fake_app_and_repo(tmp_storage, monkeypatch):
    repo = UserRepository(tmp_storage)
    app = FakeApp(repo)
    # Monkeypatch Kivy App getter to return our fake app
    from kivy import app as kivy_app
    monkeypatch.setattr(kivy_app, "App", SimpleNamespace(get_running_app=lambda: app))
    return app, repo


def test_login_flow_valid(fake_app_and_repo, monkeypatch):
    app, repo = fake_app_and_repo
    uid = repo.create_user("user1", "secret123", None)
    assert uid > 0

    screen = LoginScreen()
    screen.ids = {"username": _Text("user1"), "password": _Text("secret123")}
    msgs = []
    monkeypatch.setattr(screen, "_show_msg", lambda txt: msgs.append(txt))

    screen.do_login()
    assert app.logged is True
    assert app.switched_to == "home"
    assert any("Bienvenido" in m for m in msgs)


def test_login_flow_invalid(fake_app_and_repo, monkeypatch):
    app, repo = fake_app_and_repo
    repo.create_user("user2", "secret123", None)
    screen = LoginScreen()
    screen.ids = {"username": _Text("user2"), "password": _Text("wrong")}
    msgs = []
    monkeypatch.setattr(screen, "_show_msg", lambda txt: msgs.append(txt))

    screen.do_login()
    assert app.logged is False
    assert app.switched_to is None
    assert any("incorrectos" in m or "incorrectas" in m or "incorrecto" in m for m in msgs)


def test_register_flow_valid_and_duplicate(fake_app_and_repo, monkeypatch):
    app, repo = fake_app_and_repo

    screen = RegisterScreen()
    # Valid registration
    screen.ids = {
        "reg_username": _Text("nuevo"),
        "reg_email": _Text("a@b.com"),
        "reg_password": _Text("secret123"),
        "reg_confirm": _Text("secret123"),
    }
    msgs = []
    monkeypatch.setattr(screen, "_show_msg", lambda txt: msgs.append(txt))
    screen.do_register()
    assert app.switched_to == "login"
    assert any("inicia sesión" in m for m in msgs)

    # Duplicate username should show error
    screen2 = RegisterScreen()
    screen2.ids = {
        "reg_username": _Text("nuevo"),
        "reg_email": _Text("a@b.com"),
        "reg_password": _Text("secret123"),
        "reg_confirm": _Text("secret123"),
    }
    msgs2 = []
    monkeypatch.setattr(screen2, "_show_msg", lambda txt: msgs2.append(txt))
    screen2.do_register()
    assert any("existe" in m for m in msgs2)


def test_register_validation_errors(fake_app_and_repo, monkeypatch):
    app, repo = fake_app_and_repo

    # Short password
    s1 = RegisterScreen()
    s1.ids = {
        "reg_username": _Text("u"),
        "reg_email": _Text(""),
        "reg_password": _Text("123"),
        "reg_confirm": _Text("123"),
    }
    msgs1 = []
    monkeypatch.setattr(s1, "_show_msg", lambda txt: msgs1.append(txt))
    s1.do_register()
    assert any("al menos 6" in m for m in msgs1)

    # Mismatched passwords
    s2 = RegisterScreen()
    s2.ids = {
        "reg_username": _Text("u2"),
        "reg_email": _Text(""),
        "reg_password": _Text("abcdef"),
        "reg_confirm": _Text("xyz123"),
    }
    msgs2 = []
    monkeypatch.setattr(s2, "_show_msg", lambda txt: msgs2.append(txt))
    s2.do_register()
    assert any("no coinciden" in m for m in msgs2)


