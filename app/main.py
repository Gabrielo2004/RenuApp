from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.navigationbar import (
    MDNavigationBar,
    MDNavigationItem,
    MDNavigationItemIcon,
    MDNavigationItemLabel,
)
from kivymd.uix.fitimage import FitImage
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp
from pathlib import Path
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

        # Load shared styles and screen kvs
        Builder.load_file("assets/kv/styles.kv")
        Builder.load_file("assets/kv/home.kv")
        Builder.load_file("assets/kv/map.kv")
        Builder.load_file("assets/kv/tips.kv")
        Builder.load_file("assets/kv/challenges.kv")
        Builder.load_file("assets/kv/auth.kv")

        # Initialize local storage (SQLite)
        # Ensure assets directories exist
        Path("assets/images").mkdir(parents=True, exist_ok=True)

        self.storage = StorageService()
        self.storage.initialize_database()
        seed_if_empty(self.storage)
        sync_tip_images(self.storage)
        # Repositories
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

        # Screens
        self.screen_manager = MDScreenManager()
        self.screen_manager.add_widget(HomeScreen(name="home"))
        self.screen_manager.add_widget(MapScreen(name="map"))
        self.screen_manager.add_widget(TipsScreen(name="tips"))
        self.screen_manager.add_widget(ChallengesScreen(name="challenges"))
        self.screen_manager.add_widget(LoginScreen(name="login"))
        self.screen_manager.add_widget(RegisterScreen(name="register"))

        # Root layout structure
        root = BoxLayout(orientation="vertical")
        # Header container with MDTopAppBar and logo on the left
        header = FloatLayout(size_hint_y=None, height=dp(64))
        self.header = header
        self._header_default_height = dp(64)
        self.top_bar = MDTopAppBar()
        self.top_bar.size_hint = (1, 1)
        # Set initial headline/title in a version-tolerant way
        if hasattr(self.top_bar, "headline_text"):
            self.top_bar.headline_text = self._titles["home"]
        elif hasattr(self.top_bar, "title"):
            self.top_bar.title = self._titles["home"]
        header.add_widget(self.top_bar)

        # Logo on the left overlaying the app bar
        logo = FitImage(source="assets/images/Renü logo.png")
        logo.size_hint = (None, None)
        logo.size = (dp(90), dp(90))
        logo.pos_hint = {"x": 0.02, "center_y": 0.5}
        header.add_widget(logo)

        # Account button aligned to the right via AnchorLayout to avoid clipping
        from kivymd.uix.button import MDButton, MDButtonIcon
        self.account_btn = MDButton(style="tonal")
        self.account_btn.size_hint = (None, None)
        self.account_btn.width = dp(40)
        self.account_btn.height = dp(40)
        self.account_btn.add_widget(MDButtonIcon(icon="account-circle"))
        self.account_btn.bind(on_release=lambda _w: self.open_account_menu())
        self.account_btn.opacity = 0
        self.account_btn.disabled = True
        header.add_widget(self.account_btn)
        self.account_btn.pos_hint = {"right": 0.965, "center_y": 0.5}

        root.add_widget(header)
        root.add_widget(self.screen_manager)

        # Bottom navigation
        self.nav_bar = MDNavigationBar()
        self.nav_bar.bind(on_switch_tabs=self.on_switch_tabs)

        # Map navigation items to screen names
        self._nav_map = {}

        item_home = MDNavigationItem()
        item_home.add_widget(MDNavigationItemIcon(icon="home"))
        item_home.add_widget(MDNavigationItemLabel(text="Inicio"))
        self._nav_map[item_home] = "home"
        self.nav_bar.add_widget(item_home)

        item_map = MDNavigationItem()
        item_map.add_widget(MDNavigationItemIcon(icon="map"))
        item_map.add_widget(MDNavigationItemLabel(text="Mapa"))
        self._nav_map[item_map] = "map"
        self.nav_bar.add_widget(item_map)

        item_tips = MDNavigationItem()
        item_tips.add_widget(MDNavigationItemIcon(icon="lightbulb-on-outline"))
        item_tips.add_widget(MDNavigationItemLabel(text="Consejos"))
        self._nav_map[item_tips] = "tips"
        self.nav_bar.add_widget(item_tips)

        item_challenges = MDNavigationItem()
        item_challenges.add_widget(MDNavigationItemIcon(icon="trophy-outline"))
        item_challenges.add_widget(MDNavigationItemLabel(text="Desafíos"))
        self._nav_map[item_challenges] = "challenges"
        self.nav_bar.add_widget(item_challenges)
        root.add_widget(self.nav_bar)

        # Default route based on persisted session
        self.is_logged_in = False
        current_uid = self.users_repo.get_current_user_id()
        if current_uid:
            self.set_logged_in(True)
            self.switch_to("home")
        else:
            self.switch_to("login")
        self._update_nav_visibility()
        return root

    # Navigation helpers
    def switch_to(self, screen_name: str) -> None:
        if screen_name in self._titles:
            self.screen_manager.current = screen_name
            # Update top bar label compatibly
            if hasattr(self.top_bar, "headline_text"):
                self.top_bar.headline_text = self._titles[screen_name]
            elif hasattr(self.top_bar, "title"):
                self.top_bar.title = self._titles[screen_name]
        else:
            # for auth screens (login/register)
            self.screen_manager.current = screen_name
            if hasattr(self.top_bar, "headline_text"):
                self.top_bar.headline_text = "Renü"
            elif hasattr(self.top_bar, "title"):
                self.top_bar.title = "Renü"
        self._update_nav_visibility()

    def on_switch_tabs(self, bar, item, *args) -> None:
        name = self._nav_map.get(item)
        if name:
            self.switch_to(name)

    # Auth helpers
    def set_logged_in(self, value: bool) -> None:
        self.is_logged_in = value
        # account button visibility
        self.account_btn.opacity = 1 if value else 0
        self.account_btn.disabled = not value
        # if logging out, go to login
        if not value:
            self.switch_to("login")

    def _update_nav_visibility(self) -> None:
        auth = self.screen_manager.current in ("login", "register")
        if auth:
            self.nav_bar.opacity = 0
            self.nav_bar.disabled = True
            self.nav_bar.size_hint_y = None
            self.nav_bar.height = 0
            # hide header completely on auth screens
            self.header.opacity = 0
            self.header.size_hint_y = None
            self.header.height = 0
        else:
            self.nav_bar.opacity = 1
            self.nav_bar.disabled = False
            self.nav_bar.size_hint_y = None
            # give enough height so icon y texto no se solapen
            self.nav_bar.height = dp(84)
            # show header
            self.header.opacity = 1
            self.header.size_hint_y = None
            self.header.height = self._header_default_height
            self.header.height = self._header_default_height

    def open_account_menu(self) -> None:
        # For KivyMD v2 compatibility, use Snackbar instead of Dialog
        # Clear persisted session
        try:
            self.users_repo.clear_session()
        except Exception:
            pass
        self.set_logged_in(False)
        try:
            MDSnackbar(MDSnackbarText(text="Sesión cerrada")) .open()
        except Exception:
            pass

    


