# app/screens/home.py — VERSIÓN FINAL

from kivy.app import App
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.carousel import Carousel
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage
from kivy.graphics import Color, Rectangle
from kivy.metrics import sp
from kivy.clock import Clock
from pathlib import Path
from os.path import exists
from kivymd.uix.label import MDLabel


class HomeScreen(MDScreen):

    weekly_title = StringProperty("")
    weekly_desc = StringProperty("")
    weekly_target = NumericProperty(1)
    weekly_progress = NumericProperty(0)
    progress_text = StringProperty("0/1")
    progress_percent = NumericProperty(0.0)
    _weekly_id = NumericProperty(0)

    def on_kv_post(self, _):
        app = App.get_running_app()

        weekly = app.challenges_repo.get_weekly()
        if weekly:
            cid, t, d, target, unit, pts, is_weekly = weekly
            self._weekly_id = cid
            self.weekly_title = t
            self.weekly_desc = d
            self.weekly_target = target
            self.weekly_progress = app.challenges_repo.get_progress(cid)
            self._compute_progress()

        self._load_carousel()
        self._update_progress_ui()

    # CARRUSEL
    def _load_carousel(self):
        images_dir = Path("assets/images")
        exts = {".jpg", ".jpeg", ".png", ".webp"}

        image_paths = [
            str(p) for p in sorted(images_dir.iterdir())
            if p.suffix.lower() in exts and "logo" not in p.name.lower()
        ] if images_dir.exists() else []

        carousel = self.ids.photos_carousel
        carousel.clear_widgets()

        tips = App.get_running_app().tips_repo.featured(limit=len(image_paths))

        for i, img_path in enumerate(image_paths):
            slide = FloatLayout()

            if exists(img_path):
                bg = FitImage(source=img_path, allow_stretch=True, keep_ratio=False)
                bg.size_hint = (1, 1)
                slide.add_widget(bg)

            overlay = MDBoxLayout(
                orientation="vertical",
                padding="16dp",
                spacing="6dp",
                size_hint=(1, None),
                height=140,
                pos_hint={"x": 0, "y": 0}
            )

            with overlay.canvas.before:
                Color(0, 0, 0, 0.40)
                rect = Rectangle(size=overlay.size, pos=overlay.pos)

            def sync(_, __, r=rect, ov=overlay):
                r.pos = ov.pos
                r.size = ov.size

            overlay.bind(pos=sync, size=sync)
            sync(None, None)

            title = tips[i][1] if i < len(tips) else ""
            body = tips[i][2] if i < len(tips) else ""

            if title:
                h1 = MDLabel(
                    text=title,
                    font_size=sp(24),
                    bold=True,
                    text_color=(1,1,1,1),
                    halign="left",
                    size_hint_y=None
                )
                h1.bind(texture_size=lambda inst,v: setattr(inst,"height",v[1]))
                overlay.add_widget(h1)

            if body:
                p = MDLabel(
                    text=body,
                    font_size=sp(16),
                    text_color=(1,1,1,1),
                    halign="left",
                    size_hint_y=None
                )
                p.bind(texture_size=lambda inst,v: setattr(inst,"height",v[1]))
                overlay.add_widget(p)

            slide.add_widget(overlay)
            carousel.add_widget(slide)

        if len(image_paths) > 1:
            if hasattr(self, "_carousel_ev"):
                self._carousel_ev.cancel()
            self._carousel_ev = Clock.schedule_interval(
                lambda dt: carousel.load_next(), 5
            )

    # PROGRESO
    def register_recycling(self):
        if not self._weekly_id:
            return

        if self.weekly_progress >= self.weekly_target:
            return

        app = App.get_running_app()
        self.weekly_progress = app.challenges_repo.increment_progress(self._weekly_id, 1)
        self._compute_progress()
        self._update_progress_ui()

    def reset_weekly_progress(self):
        if not self._weekly_id:
            return
        app = App.get_running_app()
        app.challenges_repo.set_progress(self._weekly_id, 0)
        self.weekly_progress = 0
        self._compute_progress()
        self._update_progress_ui()

    def _compute_progress(self):
        t = max(1, int(self.weekly_target))
        p = int(self.weekly_progress)
        self.progress_percent = min(100, (p / t) * 100)
        self.progress_text = f"{p}/{t}"

    def _update_progress_ui(self):
        bar = self.ids.weekly_progress
        txt = self.ids.weekly_progress_label
        bar.value = self.progress_percent
        txt.text = self.progress_text
