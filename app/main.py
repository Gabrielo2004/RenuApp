from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from pathlib import Path

from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.navigationbar import (
    MDNavigationBar,
    MDNavigationItem,
    MDNavigationItemIcon,
    MDNavigationItemLabel,
)
from kivymd.uix.button import MDIconButton
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

from .theme import setup_theme
from .services.storage import StorageService
from .services.seed import seed_if_empty, sync_tip_images
from .services.repositories.challenges import ChallengesRepository
from .services.repositories.tips import TipsRepository
from .services.repositories.users import UserRepository
from .services.repositories.points import PointsRepository
from .screens.home import HomeScreen
from .screens.map import MapScreen
from .screens.tips import TipsScreen
from .screens.challenges import ChallengesScreen
from .screens.auth import LoginScreen, RegisterScreen


class RenuApp(MDApp):
    def build(self):
        setup_theme(self)

        # Cargar KV
        Builder.load_file("assets/kv/styles.kv")
        Builder.load_file("assets/kv/home.kv")
        Builder.load_file("assets/kv/map.kv")
        Builder.load_file("assets/kv/tips.kv")
        Builder.load_file("assets/kv/challenges.kv")
        Builder.load_file("assets/kv/auth.kv")

        # Inicializar almacenamiento / seed
        Path("assets/images").mkdir(parents=True, exist_ok=True)

        self.storage = StorageService()
        self.storage.initialize_database()
        seed_if_empty(self.storage)
        sync_tip_images(self.storage)

        self.challenges_repo = ChallengesRepository(self.storage)
        self.tips_repo = TipsRepository(self.storage)
        self.users_repo = UserRepository(self.storage)
        self.points_repo = PointsRepository(self.storage)

        self._titles = {
            "home": "Renü",
            "map": "Mapa",
            "tips": "Consejos Eco",
            "challenges": "Desafíos",
        }

        # Screen manager
        self.screen_manager = MDScreenManager()
        self.screen_manager.add_widget(HomeScreen(name="home"))
        self.screen_manager.add_widget(MapScreen(name="map"))
        self.screen_manager.add_widget(TipsScreen(name="tips"))
        self.screen_manager.add_widget(ChallengesScreen(name="challenges"))
        self.screen_manager.add_widget(LoginScreen(name="login"))
        self.screen_manager.add_widget(RegisterScreen(name="register"))

        # Layout raíz
        root = BoxLayout(orientation="vertical")

        # ---------- HEADER (barra superior + botón logout) ----------
        header = FloatLayout(size_hint_y=None, height=dp(64))
        self.header = header

        self.top_bar = MDTopAppBar()
        self.top_bar.size_hint = (1, 1)
        self.top_bar.elevation = 3

        if hasattr(self.top_bar, "headline_text"):
            self.top_bar.headline_text = "Renü"
        else:
            self.top_bar.title = "Renü"

        header.add_widget(self.top_bar)
        from kivymd.uix.fitimage import FitImage

        logo = FitImage(source="assets/images/Renü logo.png")
        logo.size_hint = (None, None)
        logo.size = (dp(90), dp(90))
        logo.pos_hint = {"x": 0.02, "center_y": 0.5}
        header.add_widget(logo)

        # Botón de CERRAR SESIÓN como icono a la derecha
        self.logout_btn = MDIconButton(
            icon="logout",
            pos_hint={"right": 0.97, "center_y": 0.5},
        )
        self.logout_btn.on_release = self.open_account_menu
        header.add_widget(self.logout_btn)

        root.add_widget(header)
        root.add_widget(self.screen_manager)

        # ---------- BARRA DE NAVEGACIÓN INFERIOR ----------
        self.nav_bar = MDNavigationBar()
        self._nav_map = {}

        def add_item(icon, text, screen_name):
            item = MDNavigationItem()
            item.add_widget(MDNavigationItemIcon(icon=icon))
            item.add_widget(MDNavigationItemLabel(text=text))
            self.nav_bar.add_widget(item)
            self._nav_map[item] = screen_name

        add_item("home", "Inicio", "home")
        add_item("map", "Mapa", "map")
        add_item("lightbulb-on-outline", "Consejos", "tips")
        add_item("trophy-outline", "Desafíos", "challenges")

        self.nav_bar.bind(on_switch_tabs=self.on_switch_tabs)
        root.add_widget(self.nav_bar)

        # ---------- Sesión persistida ----------
        current_uid = self.users_repo.get_current_user_id()
        if current_uid:
            # Usuario ya logeado
            self.show_authenticated_ui()
            self.switch_to("home")
        else:
            # Usuario NO logeado → ocultar UI
            self.show_unauthenticated_ui()
            self.switch_to("login")

        return root

    # ---------------- NAVEGACIÓN ----------------
    def switch_to(self, screen_name: str) -> None:
        self.screen_manager.current = screen_name
        if screen_name in self._titles:
            if hasattr(self.top_bar, "headline_text"):
                self.top_bar.headline_text = self._titles[screen_name]
            else:
                self.top_bar.title = self._titles[screen_name]

    def on_switch_tabs(self, bar, item, *args) -> None:
        name = self._nav_map.get(item)
        if name:
            self.switch_to(name)

    # ---------------- LOGOUT ----------------
    def open_account_menu(self, *args):
    # limpiar sesión
        try:
            self.users_repo.clear_session()
        except Exception:
            pass

        # ✔ Ocultar UI de usuario autenticado
        self.show_unauthenticated_ui()

        # ✔ Ir al login
        self.switch_to("login")

        # Snackbar opcional
        try:
            MDSnackbar(MDSnackbarText(text="Sesión cerrada")).open()
        except Exception:
            pass

    # -------------------------------------------
    #   CONTROL VISUAL DE SESIÓN
    # -------------------------------------------
    def show_authenticated_ui(self):
        # Mostrar barra superior
        self.top_bar.opacity = 1
        self.top_bar.height = dp(64)
        self.header.size_hint_y = None
        self.header.height = dp(64)

        # Mostrar botón logout
        self.logout_btn.opacity = 1
        self.logout_btn.disabled = False

        # Mostrar barra inferior
        self.nav_bar.opacity = 1
        self.nav_bar.disabled = False
        self.nav_bar.height = dp(84)

    def show_unauthenticated_ui(self):
        # Ocultar barra superior
        self.top_bar.opacity = 0
        self.top_bar.height = 0
        self.header.height = 0

        # Ocultar botón logout
        self.logout_btn.opacity = 0
        self.logout_btn.disabled = True

        # Ocultar barra inferior
        self.nav_bar.opacity = 0
        self.nav_bar.disabled = True
        self.nav_bar.height = 0
