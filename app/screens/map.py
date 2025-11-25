from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivy.metrics import dp
import webbrowser

from kivy_garden.mapview import MapView, MapMarker


# -------------------------
# Normalizador de texto
# -------------------------
def normalize(s: str):
    s = s.lower()
    s = s.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    return s.strip()


class MapScreen(MDScreen):

    # -------------------------
    # Mapa de equivalencias
    # -------------------------
    FILTER_MAP = {
        "papel": ["papel", "carton"],
        "carton": ["carton", "papel"],
        "plastico": ["plastico"],
        "vidrio": ["vidrio"],
        "latas": ["latas"],
    }

    # -------------------------
    # Carga de pantalla
    # -------------------------
    def on_kv_post(self, base_widget):
        self._active_filters = set()
        self._selected_point = None

        self._setup_map()
        self._load_points_from_db()
        self._refresh_markers_and_list()

    # -------------------------
    # Crear mapa
    # -------------------------
    def _setup_map(self):
        container = self.ids.get("map_container")
        if not container:
            return

        self.mapview = MapView(
            zoom=13,
            lat=-38.739,
            lon=-72.598
        )
        self.mapview.size_hint = (1, 1)

        container.add_widget(self.mapview)

    # -------------------------
    # Refrescar marcadores + lista
    # -------------------------
    def _refresh_markers_and_list(self):

        # Normalizar filtros activos
        active = [normalize(m) for m in self._active_filters]

        # Expandir equivalencias
        expected_materials = set()
        for a in active:
            expected_materials.update(self.FILTER_MAP.get(a, []))

        # Si no hay filtros: mostrar todo
        if not expected_materials:
            points = list(self._all_points)
        else:
            points = []
            for p in self._all_points:
                mats = [normalize(m) for m in p.get("materials", [])]

                # Al menos un material coincide
                if any(m in expected_materials for m in mats):
                    points.append(p)

        # -------------------------
        # Actualizar marcadores del mapa
        # -------------------------
        for child in list(self.mapview.children):
            if isinstance(child, MapMarker):
                self.mapview.remove_widget(child)

        for p in points:
            marker = MapMarker(lat=p["lat"], lon=p["lon"])
            marker.bind(on_release=lambda _m, pt=p: self._select_point(pt))
            self.mapview.add_widget(marker)

        if points:
            self.mapview.center_on(points[0]["lat"], points[0]["lon"])

        # -------------------------
        # Actualizar lista de cards
        # -------------------------
        list_box = self.ids.points_list
        list_box.clear_widgets()

        for p in points:
            list_box.add_widget(self._build_point_card(p))

    # -------------------------
    # Seleccionar punto del mapa
    # -------------------------
    def _select_point(self, point):
        self._selected_point = point
        self.mapview.center_on(point["lat"], point["lon"])

    # -------------------------
    # Filtros desde botones
    # -------------------------
    def toggle_filter(self, material):
        material = normalize(material)

        if material in self._active_filters:
            self._active_filters.remove(material)
        else:
            self._active_filters.add(material)

        self._refresh_markers_and_list()

    # -------------------------
    # Ruta en Google Maps
    # -------------------------
    def open_route(self):
        if not self._selected_point:
            return

        lat = self._selected_point["lat"]
        lon = self._selected_point["lon"]

        url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
        webbrowser.open(url)

    # -------------------------
    # Cargar DB
    # -------------------------
    def _load_points_from_db(self):
        from kivy.app import App
        app = App.get_running_app()

        try:
            self._all_points = app.points_repo.list_points()
        except:
            self._all_points = []

    # -------------------------
    # Construcción de cards
    # -------------------------
    def _build_point_card(self, p: dict) -> MDCard:
        from kivy.metrics import sp as _sp

        card = MDCard(radius=[14], padding=dp(16), size_hint_y=None, elevation=3)

        row = MDBoxLayout(orientation="horizontal", spacing=dp(12))
        row.size_hint_y = None
        row.bind(minimum_height=lambda inst, val: setattr(row, "height", val))

        def _wrap(lbl, container, align="left"):
            lbl.size_hint_y = None
            lbl.halign = align
            lbl.valign = "top"
            lbl.text_size = (container.width, None)
            container.bind(width=lambda _i, w: setattr(lbl, "text_size", (w, None)))
            lbl.bind(texture_size=lambda inst, val: setattr(lbl, "height", val[1]))

        # COLUMN LEFT
        col_left = MDBoxLayout(orientation="vertical", spacing=dp(6))
        col_left.size_hint_x = 0.68
        col_left.size_hint_y = None
        col_left.bind(minimum_height=lambda inst, val: setattr(col_left, "height", val))

        name_lbl = MDLabel(text=p.get("name", ""))
        name_lbl.font_size = _sp(16)
        name_lbl.max_lines = 2
        _wrap(name_lbl, col_left, "left")
        col_left.add_widget(name_lbl)

        addr_lbl = MDLabel(text=p.get("address", ""), theme_text_color="Secondary")
        addr_lbl.font_size = _sp(14)
        _wrap(addr_lbl, col_left, "left")
        col_left.add_widget(addr_lbl)

        chips = MDBoxLayout(spacing=dp(6))
        chips.size_hint_y = None
        chips.bind(minimum_height=lambda inst, val: setattr(chips, "height", val))

        for m in p.get("materials", []):
            chip = MDCard(padding=dp(6), radius=[12])
            chip.add_widget(MDLabel(text=m))
            chips.add_widget(chip)

        col_left.add_widget(chips)

        # COLUMN RIGHT
        col_right = MDBoxLayout(orientation="vertical", spacing=dp(6), padding=[0, dp(6), 0, dp(6)])
        col_right.size_hint_x = 0.32
        col_right.size_hint_y = None
        col_right.bind(minimum_height=lambda inst, val: setattr(col_right, "height", val))

        dist_lbl = MDLabel(text=f"{p.get('distance_km', 0)} km", theme_text_color="Secondary")
        _wrap(dist_lbl, col_right, "center")
        col_right.add_widget(dist_lbl)

        hrs_lbl = MDLabel(text=p.get("hours", ""), theme_text_color="Secondary")
        _wrap(hrs_lbl, col_right, "center")
        col_right.add_widget(hrs_lbl)

        row.add_widget(col_left)
        row.add_widget(col_right)
        card.add_widget(row)

        def update_height(*_):
            card.height = row.minimum_height + dp(32)

        row.bind(minimum_height=lambda *_: update_height())
        from kivy.clock import Clock
        Clock.schedule_once(lambda _dt: update_height())

        card.bind(on_release=lambda _w: self._select_point(p))

        return card
