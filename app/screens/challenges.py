from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivy.metrics import dp, sp
from typing import List, Dict


class ChallengesScreen(MDScreen):
    def on_kv_post(self, base_widget):
        self._filter = "Todos"
        self._load_from_db()
        self._rebuild_list()

    # --- Filters ---
    def apply_filter(self, name: str):
        self._filter = name
        self._rebuild_list()

    # --- Build list of cards ---
    def _rebuild_list(self):
        container = self.ids.get("challenges_list")
        if container is None:
            return

        container.clear_widgets()

        # Filtering
        if self._filter == "Completados":
            items = [c for c in self._challenges if c["progress"] >= c["target"]]
        else:
            items = [c for c in self._challenges if self._filter in ("Todos", c["period_label"])]

        for ch in items:
            container.add_widget(self._build_card(ch))

    # --- Build a single card ---
    def _build_card(self, ch: Dict) -> MDCard:
        card = MDCard(
            radius=[18],
            padding=dp(14),
            elevation=2,
            size_hint_y=None
        )

        root = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )
        root.bind(minimum_height=lambda inst, val: setattr(root, "height", val))

        # --- Header ---
        header = MDBoxLayout(
            spacing=dp(10),
            padding=(dp(2), 0),
            size_hint_y=None
        )
        header.bind(minimum_height=lambda inst, val: setattr(header, "height", val))

        # Icon
        header.add_widget(
            MDLabel(
                text="🏆",
                font_size=sp(22),
                size_hint=(None, None),
                height=sp(22),
                width=sp(22),
                halign="center",
                valign="center"
            )
        )

        # Title + subtitle
        text_col = MDBoxLayout(
            orientation="vertical",
            spacing=dp(2),
            size_hint_y=None
        )
        text_col.bind(minimum_height=lambda inst, val: setattr(text_col, "height", val))

        title = MDLabel(
            text=ch["title"],
            font_size=sp(16),
            bold=True,
            halign="left",
            size_hint_y=None
        )
        title.bind(texture_size=lambda inst, val: setattr(title, "height", val[1]))

        subtitle = MDLabel(
            text=ch["subtitle"],
            theme_text_color="Secondary",
            font_size=sp(13),
            halign="left",
            size_hint_y=None
        )
        subtitle.bind(texture_size=lambda inst, val: setattr(subtitle, "height", val[1]))

        text_col.add_widget(title)
        text_col.add_widget(subtitle)
        header.add_widget(text_col)
        root.add_widget(header)

        # --- Progress bar ---
        bar = MDLinearProgressIndicator(
            value=min(100, (ch["progress"] / max(1, ch["target"])) * 100),
            height=dp(12),
            size_hint_y=None
        )
        root.add_widget(bar)

        # --- Footer ---
        footer = MDBoxLayout(
            spacing=dp(10),
            size_hint_y=None
        )
        footer.bind(minimum_height=lambda inst, val: setattr(footer, "height", val))

        # Progress label
        count = MDLabel(
            text=f"{ch['progress']}/{ch['target']}",
            theme_text_color="Secondary",
            font_size=sp(14),
            size_hint_y=None
        )
        count.bind(texture_size=lambda inst, val: setattr(count, "height", val[1]))
        footer.add_widget(count)

        # Spacer
        footer.add_widget(MDBoxLayout())

        # --- Button: Registrar / Completado ---
        btn = MDButton(
            style="filled",
            size_hint=(None, None),
            width=dp(110),
            height=dp(40),
            disabled = (ch["progress"] >= ch["target"])   # <<< Bloqueo automático
        )

        if ch["progress"] < ch["target"]:
            btn.bind(on_release=lambda _w, cid=ch["id"]: self._increment(cid))


        btn_text = MDButtonText(
            text="Registrar" if ch["progress"] < ch["target"] else "Completado"
        )
        btn.add_widget(btn_text)
        footer.add_widget(btn)

        # --- Button: Reiniciar ---
        reset_btn = MDButton(
            style="tonal",
            size_hint=(None, None),
            width=dp(110),
            height=dp(40)
        )
        reset_text = MDButtonText(text="Reiniciar")
        reset_btn.add_widget(reset_text)

        # Mostrar solo si está completado
        if ch["progress"] >= ch["target"]:
            reset_btn.opacity = 1
            reset_btn.disabled = False
        else:
            reset_btn.opacity = 0
            reset_btn.disabled = True

        reset_btn.bind(on_release=lambda _w, cid=ch["id"]: self._reset(cid))
        footer.add_widget(reset_btn)

        root.add_widget(footer)
        card.add_widget(root)

        # --------------------------
        #       AUTO HEIGHT
        # --------------------------
        from kivy.clock import Clock

        def _upd(*_):
            card.height = root.minimum_height + dp(16)

        root.bind(minimum_height=lambda *_: _upd())
        Clock.schedule_once(lambda *_: _upd())

        # --------------------------
        # FIX VISUAL DE BOTONES
        # --------------------------
        def _fix_sizes(*_):
            btn_text.texture_update()
            reset_text.texture_update()

            btn.width = max(dp(110), btn_text.texture_size[0] + dp(24))
            reset_btn.width = max(dp(110), reset_text.texture_size[0] + dp(24))

            footer.do_layout()
            root.do_layout()
            card.height = root.minimum_height + dp(16)

        Clock.schedule_once(_fix_sizes, 0)

        # Guardar referencias
        card._refs = {
            "bar": bar,
            "count": count,
            "btn": btn,
            "btn_text": btn_text,
            "reset_btn": reset_btn,
            "reset_text": reset_text,
            "ch": ch
        }

        return card

    # --- Incrementar desafío ---
    def _increment(self, challenge_id: int):
        from kivy.app import App
        app = App.get_running_app()
        new_val = app.challenges_repo.increment_progress(challenge_id, 1)

        for ch in self._challenges:
            if ch["id"] == challenge_id:
                ch["progress"] = new_val
                break

        self._rebuild_list()

    # --- Reiniciar desafío ---
    def _reset(self, challenge_id: int):
        from kivy.app import App
        app = App.get_running_app()

        app.challenges_repo.set_progress(challenge_id, 0)

        for ch in self._challenges:
            if ch["id"] == challenge_id:
                ch["progress"] = 0
                break

        self._rebuild_list()

    # --- Load DB ---
    def _load_from_db(self):
        from kivy.app import App
        app = App.get_running_app()

        rows = app.challenges_repo.list_all()
        result: List[Dict] = []

        for (cid, title, desc, period, target, unit, points, is_weekly) in rows:
            app.challenges_repo.ensure_progress_row(cid)
            prog = app.challenges_repo.get_progress(cid)

            period_label = {
                "weekly": "Semanales",
                "daily": "Diarios",
                "once": "Únicos",
            }.get(period, "Otros")

            subtitle = "Desafío semanal" if is_weekly else (desc or "Desafío")

            result.append({
                "id": int(cid),
                "title": title,
                "subtitle": subtitle,
                "target": int(target),
                "progress": int(prog),
                "period": period,
                "period_label": period_label,
                "unit": unit,
                "points": int(points or 0),
                "is_weekly": int(is_weekly or 0),
            })

        self._challenges = result
