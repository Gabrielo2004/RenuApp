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
        # Load challenges from DB (with progress)
        self._filter = "Todos"
        self._load_from_db()
        self._rebuild_list()

    # Filters
    def apply_filter(self, name: str):
        self._filter = name
        self._rebuild_list()

    # UI builders
    def _rebuild_list(self):
        container = self.ids.get("challenges_list")
        if container is None:
            return
        container.clear_widgets()
        items = [c for c in self._challenges if self._filter in ("Todos", c["period_label"]) ]
        for ch in items:
            container.add_widget(self._build_card(ch))

    def _build_card(self, ch: Dict) -> MDCard:
        card = MDCard(radius=[16], padding=dp(12), size_hint_y=None)
        root = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        root.bind(minimum_height=lambda inst, val: setattr(root, "height", val))

        # Header row with icon and texts
        header = MDBoxLayout(spacing=dp(8), size_hint_y=None)
        header.bind(minimum_height=lambda inst, val: setattr(header, "height", val))
        # Icon placeholder (avoid MDIcon import issues in KivyMD v2)
        header.add_widget(MDLabel(text="🏆", size_hint_y=None))
        text_col = MDBoxLayout(orientation="vertical", size_hint_y=None)
        text_col.bind(minimum_height=lambda inst, val: setattr(text_col, "height", val))

        title = MDLabel(text=ch["title"], font_size=sp(16))
        title.size_hint_y = None
        title.halign = "left"
        title.text_size = (title.width, None)
        title.bind(texture_size=lambda inst, val: setattr(title, "height", val[1]))
        text_col.add_widget(title)

        subtitle = MDLabel(text=ch["subtitle"], theme_text_color="Secondary", font_size=sp(14))
        subtitle.size_hint_y = None
        subtitle.halign = "left"
        subtitle.text_size = (subtitle.width, None)
        subtitle.bind(texture_size=lambda inst, val: setattr(subtitle, "height", val[1]))
        text_col.add_widget(subtitle)

        header.add_widget(text_col)
        root.add_widget(header)

        # Progress
        bar = MDLinearProgressIndicator()
        bar.size_hint_y = None
        bar.height = dp(15)
        bar.value = min(100, (ch["progress"] / max(1, ch["target"])) * 100)
        root.add_widget(bar)

        # Footer row with count and button
        footer = MDBoxLayout(spacing=dp(8), size_hint_y=None)
        footer.bind(minimum_height=lambda inst, val: setattr(footer, "height", val))
        count = MDLabel(text=f"{ch['progress']}/{ch['target']}", theme_text_color="Secondary")
        count.size_hint_y = None
        count.text_size = (count.width, None)
        count.bind(texture_size=lambda inst, val: setattr(count, "height", val[1]))
        footer.add_widget(count)
        footer.add_widget(MDBoxLayout())  # spacer
        btn = MDButton(style="filled")
        btn.bind(on_release=lambda _w, cid=ch["id"]: self._increment(cid))
        btn_text = MDButtonText(text="Registrar" if ch["progress"] < ch["target"] else "Completado")
        btn.add_widget(btn_text)
        footer.add_widget(btn)
        root.add_widget(footer)

        card.add_widget(root)

        # Keep card height in sync
        def _update_height(*_):
            card.height = root.minimum_height + dp(12)

        root.bind(minimum_height=lambda *_: _update_height())
        from kivy.clock import Clock as _Clock
        _Clock.schedule_once(lambda _dt: _update_height())
        # Store refs for updates
        card._refs = {"bar": bar, "count": count, "btn": btn, "btn_text": btn_text, "ch": ch}
        return card

    def _increment(self, challenge_id: int):
        from kivy.app import App as _App
        app = _App.get_running_app()
        new_val = app.challenges_repo.increment_progress(challenge_id, 1)
        for ch in self._challenges:
            if ch["id"] == challenge_id:
                ch["progress"] = new_val
                break
        self._rebuild_list()

    # Data loading
    def _load_from_db(self):
        from kivy.app import App as _App
        app = _App.get_running_app()
        rows = app.challenges_repo.list_all()
        result: List[Dict] = []
        for (cid, title, desc, period, target, unit, points, is_weekly) in rows:
            # Ensure progress row exists
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


