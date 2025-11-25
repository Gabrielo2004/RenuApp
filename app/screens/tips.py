from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.metrics import dp


def normalize(s: str) -> str:
    """Normaliza texto para comparaciones de filtros (minúsculas y sin tildes)."""
    s = (s or "").lower()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")]:
        s = s.replace(a, b)
    return s.strip()


class TipsScreen(MDScreen):
    def on_kv_post(self, base_widget):
        self._active_filters = set()
        self._build_tips_data()
        self._refresh_tips_list()

    # -------------------------
    # Datos estáticos de consejos (SOLO TEXTO)
    # -------------------------
    def _build_tips_data(self):
        self._all_tips = [
            {
                "title": "Separación de Plásticos",
                "text": "Aprende a identificar los diferentes tipos de plástico y sepáralos antes de llevarlos al punto limpio.",
                "tags": ["basico", "reciclaje"],
                "difficulty": "Fácil",
                "impact": "Alto impacto",
            },
            {
                "title": "Puntos Limpios Cercanos",
                "text": "Ubica y utiliza puntos limpios para reciclar papel, plástico, vidrio y metales al menos una vez al mes.",
                "tags": ["reciclaje", "basico"],
                "difficulty": "Fácil",
                "impact": "Medio impacto",
            },
            {
                "title": "Reduce el Consumo de Agua",
                "text": "Toma duchas más cortas y cierra la llave mientras te enjabonas o te cepillas los dientes.",
                "tags": ["agua", "basico"],
                "difficulty": "Fácil",
                "impact": "Alto impacto",
            },
            {
                "title": "Reutiliza Agua para Plantas",
                "text": "Usa el agua que sobró al lavar frutas o verduras para regar tus plantas.",
                "tags": ["agua", "plantas"],
                "difficulty": "Fácil",
                "impact": "Medio impacto",
            },
            {
                "title": "Desenchufa Cargadores y Regletas",
                "text": "Desconecta cargadores, regletas y equipos que no uses para evitar el consumo fantasma de energía.",
                "tags": ["energia", "basico"],
                "difficulty": "Fácil",
                "impact": "Alto impacto",
            },
            {
                "title": "Aprovecha la Luz Natural",
                "text": "Organiza tu espacio de estudio cerca de una ventana para encender menos luces durante el día.",
                "tags": ["energia"],
                "difficulty": "Fácil",
                "impact": "Medio impacto",
            },
            {
                "title": "Compostaje en Pequeños Espacios",
                "text": "Inicia un mini compost en un contenedor cerrado para restos de frutas, verduras y café.",
                "tags": ["compost", "plantas"],
                "difficulty": "Medio",
                "impact": "Alto impacto",
            },
            {
                "title": "Plantas Nativas y de Bajo Riego",
                "text": "Elige plantas nativas o xerófitas que requieran menos agua y se adapten mejor al clima local.",
                "tags": ["plantas", "agua"],
                "difficulty": "Fácil",
                "impact": "Medio impacto",
            },
            {
                "title": "Organiza tu Eco-Rincón",
                "text": "Destina una caja o sector para separar reciclaje y otro para guardar frascos o envases reutilizables.",
                "tags": ["basico", "reciclaje"],
                "difficulty": "Fácil",
                "impact": "Medio impacto",
            },
        ]

    # -------------------------
    # Lógica de filtros
    # -------------------------
    def toggle_filter(self, tag: str):
        tag_norm = normalize(tag)

        # Filtro especial "Todos": limpia filtros
        if tag_norm == "todos":
            self._active_filters.clear()
            self._refresh_tips_list()
            return

        if tag_norm in self._active_filters:
            self._active_filters.remove(tag_norm)
        else:
            self._active_filters.add(tag_norm)

        self._refresh_tips_list()

    # -------------------------
    # Refrescar lista según filtros activos
    # -------------------------
    def _refresh_tips_list(self):
        container = self.ids.get("tips_list")
        if not container:
            return

        container.clear_widgets()

        # Filtrado
        if not self._active_filters:
            tips = list(self._all_tips)
        else:
            tips = []
            for t in self._all_tips:
                t_tags = [normalize(x) for x in t.get("tags", [])]
                if any(f in t_tags for f in self._active_filters):
                    tips.append(t)

        # Crear cards
        for tip in tips:
            container.add_widget(self._build_tip_card(tip))

    # -------------------------
    # Construir card de cada consejo (SOLO TEXTO)
    # -------------------------
    def _build_tip_card(self, tip: dict) -> MDCard:
        from kivy.metrics import sp as _sp

        card = MDCard(
            radius=[16],
            padding=dp(16),
            size_hint_y=None,
            elevation=3,
        )

        root_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        root_box.bind(
            minimum_height=lambda inst, val: setattr(root_box, "height", val)
        )

        def _wrap_label(lbl, container, align="left"):
            lbl.size_hint_y = None
            lbl.halign = align
            lbl.valign = "top"
            lbl.text_size = (container.width, None)
            container.bind(width=lambda _i, w: setattr(lbl, "text_size", (w, None)))
            lbl.bind(texture_size=lambda _inst, val: setattr(lbl, "height", val[1]))

        # Título
        title_lbl = MDLabel(
            text=tip.get("title", ""),
            font_size=_sp(16),
        )
        _wrap_label(title_lbl, root_box, "left")
        root_box.add_widget(title_lbl)

        # Descripción
        desc_lbl = MDLabel(
            text=tip.get("text", ""),
            font_size=_sp(14),
            theme_text_color="Secondary",
        )
        _wrap_label(desc_lbl, root_box, "left")
        root_box.add_widget(desc_lbl)

        # Chips
        chips_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(6),
            size_hint_y=None,
        )
        chips_box.bind(
            minimum_height=lambda inst, val: setattr(chips_box, "height", val)
        )

        # dificultad e impacto
        difficulty = tip.get("difficulty")
        impact = tip.get("impact")
        if difficulty:
            chips_box.add_widget(self._build_chip(difficulty))
        if impact:
            chips_box.add_widget(self._build_chip(impact))

        # categorías (ej: Agua, Energía, Plantas...)
        tag_to_label = {
            "basico": "Básico",
            "reciclaje": "Reciclaje",
            "agua": "Agua",
            "energia": "Energía",
            "plantas": "Plantas",
            "compost": "Compost",
        }
        for t in tip.get("tags", []):
            lbl = tag_to_label.get(normalize(t))
            if lbl:
                chips_box.add_widget(self._build_chip(lbl))

        root_box.add_widget(chips_box)
        card.add_widget(root_box)

        # altura de la card según contenido
        card.size_hint_y = None

        def _update_height(*_):
            card.height = root_box.minimum_height + dp(16)

        _update_height()
        root_box.bind(minimum_height=lambda *_a, **_k: _update_height())

        return card

    def _build_chip(self, text: str) -> MDCard:
        from kivy.metrics import sp as _sp

        chip = MDCard(
            padding=dp(6),
            radius=[12],
            size_hint_y=None,
            elevation=0,
        )
        lbl = MDLabel(
            text=text,
            font_size=_sp(12),
            halign="center",
        )
        chip.add_widget(lbl)
        return chip
