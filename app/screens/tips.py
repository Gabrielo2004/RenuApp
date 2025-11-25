from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.metrics import dp


def normalize(s: str) -> str:
    """Normaliza texto para comparaciones de filtros (minúsculas y sin tildes)."""
    s = (s or "").lower()
    s = s.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    return s.strip()


class TipsScreen(MDScreen):
    def on_kv_post(self, base_widget):
        self._active_filters = set()
        self._build_tips_data()
        self._refresh_tips_list()

    # -------------------------
    # Datos estáticos de consejos
    # -------------------------
    def _build_tips_data(self):
        # Cada tip tiene: title, text, tags (para filtros), difficulty, impact
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
        if not hasattr(self, "_all_tips"):
            self._build_tips_data()

        # Filtrado
        if not self._active_filters:
            tips = list(self._all_tips)
        else:
            tips = []
            for t in self._all_tips:
                t_tags = [normalize(x) for x in t.get("tags", [])]
                if any(f in t_tags for f in self._active_filters):
                    tips.append(t)

        # Contenedor de cards
        container = self.ids.get("tips_list")
        if container is None:
            return

        container.clear_widgets()
        for tip in tips:
            container.add_widget(self._build_tip_card(tip))

    # -------------------------
    # Construir card de cada consejo
    # -------------------------
    def _build_tip_card(self, tip: dict) -> MDCard:
        from kivy.metrics import sp as _sp
        from kivy.clock import Clock

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

        # Chips (dificultad, impacto, categorías principales)
        chips_box = MDBoxLayout(
            spacing=dp(6),
            size_hint_y=None,
        )
        chips_box.bind(
            minimum_height=lambda inst, val: setattr(chips_box, "height", val)
        )

        # Dificultad e impacto
        difficulty = tip.get("difficulty", "")
        impact = tip.get("impact", "")
        if difficulty:
            chips_box.add_widget(self._build_chip(difficulty))
        if impact:
            chips_box.add_widget(self._build_chip(impact))

        # Categorías (ej: Reciclaje, Agua, Energía, Plantas, Compost)
        tag_to_label = {
            "basico": "Básico",
            "reciclaje": "Reciclaje",
            "agua": "Agua",
            "energia": "Energía",
            "plantas": "Plantas",
            "compost": "Compost",
        }
        for t in tip.get("tags", []):
            label = tag_to_label.get(normalize(t))
            if label:
                chips_box.add_widget(self._build_chip(label))

        root_box.add_widget(chips_box)
        card.add_widget(root_box)

        def _update_card_height(*_):
            card.height = root_box.minimum_height + dp(16)

        root_box.bind(minimum_height=lambda *_a, **_k: _update_card_height())
        Clock.schedule_once(lambda _dt: _update_card_height())

        return card

    def _build_chip(self, text: str) -> MDCard:
        from kivy.metrics import sp as _sp

        chip = MDCard(
            padding=dp(6),
            radius=[12],
            size_hint_y=None,
            elevation=0,
        )
        label = MDLabel(
            text=text,
            font_size=_sp(12),
            halign="center",
        )
        chip.add_widget(label)
        chip.bind(
            minimum_height=lambda inst, val: setattr(chip, "height", label.texture_size[1] + dp(8))
        )
        return chip
