from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivy.metrics import dp
from kivy.utils import platform
import webbrowser

try:
    from kivy_garden.mapview import MapView, MapMarker
except Exception:  # pragma: no cover - fallback when not installed
    MapView = None
    MapMarker = None


class MapScreen(MDScreen):
    def on_kv_post(self, base_widget):
        # Setup map
        self._setup_map()
        # Load points from DB
        self._load_points_from_db()
        self._selected_point = None
        self._active_filters = set()
        self._refresh_markers_and_list()

    # UI wiring
    def _setup_map(self):
        container = self.ids.get("map_container")
        if MapView is None or container is None:
            return
        self.mapview = MapView(zoom=13, lat=-38.739, lon=-72.598)
        container.add_widget(self.mapview)

    def _refresh_markers_and_list(self):
        # Filter points
        if self._active_filters:
            points = [
                p for p in self._all_points if any(m in self._active_filters for m in p["materials"])
            ]
        else:
            points = list(self._all_points)

        # Markers
        if MapView is not None and hasattr(self, "mapview"):
            self.mapview.clear_widgets()
            for p in points:
                marker = MapMarker(lat=p["lat"], lon=p["lon"])  # default marker
                marker.bind(on_release=lambda _m, pt=p: self._select_point(pt))
                self.mapview.add_widget(marker)
            if points:
                self.mapview.center_on(points[0]["lat"], points[0]["lon"])  # center on first

        # List
        list_box = self.ids.get("points_list")
        if list_box is None:
            return
        list_box.clear_widgets()
        for p in points:
            card = self._build_point_card(p)
            list_box.add_widget(card)

    # Builder to ensure exact same structure for all cards
    def _build_point_card(self, p: dict) -> MDCard:
        from kivy.metrics import sp as _sp
        card = MDCard(radius=[14], padding=dp(16), size_hint_y=None, elevation=3)

        row = MDBoxLayout(orientation="horizontal", spacing=dp(12))
        row.size_hint_y = None
        row.bind(minimum_height=lambda inst, val: setattr(row, "height", val))

        def _wrap_label(lbl, container, align="left"):
            lbl.size_hint_y = None
            lbl.halign = align
            lbl.valign = "top"
            lbl.text_size = (container.width, None)
            container.bind(width=lambda _i, w: setattr(lbl, "text_size", (w, None)))
            lbl.bind(texture_size=lambda inst, val: setattr(lbl, "height", val[1]))

        # Left column
        col_left = MDBoxLayout(orientation="vertical", spacing=dp(6))
        col_left.size_hint_x = 0.68
        col_left.size_hint_y = None
        col_left.bind(minimum_height=lambda inst, val: setattr(col_left, "height", val))

        name_lbl = MDLabel(text=p.get("name", ""))
        name_lbl.font_size = _sp(16)
        name_lbl.shorten = True
        name_lbl.max_lines = 2
        _wrap_label(name_lbl, col_left, "left")
        col_left.add_widget(name_lbl)

        addr_lbl = MDLabel(text=p.get("address", ""), theme_text_color="Secondary")
        addr_lbl.font_size = _sp(14)
        addr_lbl.shorten = True
        addr_lbl.max_lines = 2
        _wrap_label(addr_lbl, col_left, "left")
        col_left.add_widget(addr_lbl)

        chips = MDBoxLayout(spacing=dp(6))
        chips.size_hint_y = None
        chips.bind(minimum_height=lambda inst, val: setattr(chips, "height", val))
        for m in p.get("materials", []):
            chip = MDCard(padding=dp(6), radius=[12])
            chip.add_widget(MDLabel(text=m))
            chips.add_widget(chip)
        col_left.add_widget(chips)

        # Right column
        col_right = MDBoxLayout(orientation="vertical", spacing=dp(6), padding=[0, dp(6), 0, dp(6)])
        col_right.size_hint_x = 0.32
        col_right.size_hint_y = None
        col_right.bind(minimum_height=lambda inst, val: setattr(col_right, "height", val))

        dist_lbl = MDLabel(text=f"{p.get('distance_km', 0)} km", theme_text_color="Secondary")
        dist_lbl.shorten = True
        dist_lbl.max_lines = 1
        _wrap_label(dist_lbl, col_right, "center")
        hrs_lbl = MDLabel(text=p.get("hours", ""), theme_text_color="Secondary")
        hrs_lbl.shorten = True
        hrs_lbl.max_lines = 1
        _wrap_label(hrs_lbl, col_right, "center")
        col_right.add_widget(dist_lbl)
        col_right.add_widget(hrs_lbl)

        row.add_widget(col_left)
        row.add_widget(col_right)
        card.add_widget(row)

        # Click behavior
        card.bind(on_release=lambda _w: self._select_point(p))

        # Card height from content
        def _update_card_height(*_):
            card.height = row.minimum_height + dp(32)

        row.bind(minimum_height=lambda *_: _update_card_height())
        from kivy.clock import Clock as _Clock
        _Clock.schedule_once(lambda _dt: _update_card_height())
        return card

    # Interactions
    def _select_point(self, point):
        self._selected_point = point
        if MapView is not None and hasattr(self, "mapview"):
            self.mapview.center_on(point["lat"], point["lon"])

    def toggle_filter(self, material: str):
        if material in self._active_filters:
            self._active_filters.remove(material)
        else:
            self._active_filters.add(material)
        self._refresh_markers_and_list()

    # Data loading
    def _load_points_from_db(self):
        from kivy.app import App as _App
        app = _App.get_running_app()
        try:
            self._all_points = app.points_repo.list_points()
        except Exception:
            self._all_points = []

    def open_route(self):
        if not self._selected_point:
            return
        lat = self._selected_point["lat"]
        lon = self._selected_point["lon"]
        url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
        webbrowser.open(url)


