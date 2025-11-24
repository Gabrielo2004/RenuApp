from kivy.app import App
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.carousel import Carousel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage
from kivy.graphics import Color, Rectangle
from kivy.metrics import sp
from kivy.clock import Clock
from pathlib import Path
from os.path import exists


class HomeScreen(MDScreen):

    weekly_title = StringProperty("")
    weekly_desc = StringProperty("")
    weekly_target = NumericProperty(1)
    weekly_progress = NumericProperty(0)
    progress_text = StringProperty("0/1")
    progress_percent = NumericProperty(0.0)
    _weekly_id = NumericProperty(0)

    def on_kv_post(self, base_widget):
        app = App.get_running_app()

        # --- 1. Cargar desafío semanal ---
        weekly = app.challenges_repo.get_weekly()
        if weekly:
            cid, title, desc, target, unit, points, is_weekly = weekly
            self._weekly_id = cid
            self.weekly_title = title
            self.weekly_desc = desc
            self.weekly_target = target
            self.weekly_progress = app.challenges_repo.get_progress(cid)
            self._recompute_progress()

        # --- 2. Cargar carrusel de imágenes ---
        self._load_carousel()

        # --- 3. Actualizar barra de progreso ---
        self._update_ui_progress()

    def _load_carousel(self):
        images_dir = Path("assets/images")
        exts = {".jpg", ".jpeg", ".png", ".webp"}

        image_paths = []
        if images_dir.exists():
            for p in sorted(images_dir.iterdir()):
                if p.suffix.lower() in exts and "logo" not in p.name.lower():
                    image_paths.append(str(p))

        carousel: Carousel = self.ids.get("photos_carousel")

        if carousel is None:
            return

        carousel.clear_widgets()

        # Consejos destacados asociados
        app = App.get_running_app()
        tips = app.tips_repo.featured(limit=len(image_paths))

        for idx, img_path in enumerate(image_paths):
            slide = FloatLayout()

            if exists(img_path):
                bg = FitImage(source=img_path, allow_stretch=True, keep_ratio=False)
                bg.size_hint = (1, 1)
                slide.add_widget(bg)

            # Overlay oscuro con texto
            overlay = MDBoxLayout(
                orientation="vertical",
                padding="16dp",
                spacing="6dp",
                size_hint=(1, None),
                height=140,
                pos_hint={"x": 0, "y": 0}
            )

            # Fondo negro transparente
            with overlay.canvas.before:
                Color(0, 0, 0, 0.40)
                rect = Rectangle(size=overlay.size, pos=overlay.pos)

            def sync_rect(instance, value, r=rect, ov=overlay):
                r.pos = ov.pos
                r.size = ov.size

            overlay.bind(pos=sync_rect, size=sync_rect)
            sync_rect(None, None)

            # Título del tip
            if idx < len(tips):
                title, desc = tips[idx][1], tips[idx][2]
            else:
                title, desc = "", ""

            from kivymd.uix.label import MDLabel

            if title:
                lbl = MDLabel(
                    text=title,
                    text_color=(1, 1, 1, 1),
                    font_size=sp(21),
                    halign="left",
                    size_hint_y=None
                )
                lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
                overlay.add_widget(lbl)

            if desc:
                desc_lbl = MDLabel(
                    text=desc,
                    text_color=(1, 1, 1, 1),
                    font_size=sp(15),
                    halign="left",
                    size_hint_y=None
                )
                desc_lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
                overlay.add_widget(desc_lbl)

            slide.add_widget(overlay)
            carousel.add_widget(slide)

        # Autoplay
        if len(image_paths) > 1:
            if hasattr(self, "_carousel_ev"):
                self._carousel_ev.cancel()
            self._carousel_ev = Clock.schedule_interval(
                lambda dt: carousel.load_next(), 5
            )

    def register_recycling(self):
        if not self._weekly_id:
            return
        app = App.get_running_app()
        self.weekly_progress = app.challenges_repo.increment_progress(self._weekly_id, 1)
        self._recompute_progress()
        self._update_ui_progress()

    def _recompute_progress(self):
        target = max(1, int(self.weekly_target))
        progress = int(self.weekly_progress)
        self.progress_percent = min(100, (progress / target) * 100)
        self.progress_text = f"{progress}/{target}"

    def _update_ui_progress(self):
        bar = self.ids.get("weekly_progress")
        lbl = self.ids.get("weekly_progress_label")
        if bar:
            bar.value = self.progress_percent
        if lbl:
            lbl.text = self.progress_text
