from kivy.app import App
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.carousel import Carousel
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.fitimage import FitImage
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.graphics import Color, Rectangle
from os.path import exists
from pathlib import Path
from kivy.clock import Clock
from kivy.metrics import sp


class HomeScreen(MDScreen):
    weekly_title = StringProperty("")
    weekly_desc = StringProperty("")
    weekly_target = NumericProperty(1)
    weekly_progress = NumericProperty(0)
    _weekly_id = NumericProperty(0)
    progress_text = StringProperty("0/1")
    progress_percent = NumericProperty(0.0)

    def on_kv_post(self, base_widget):
        app = App.get_running_app()
        # Weekly challenge
        weekly = app.challenges_repo.get_weekly()
        if weekly:
            (cid, title, desc, target, unit, points, is_weekly) = weekly
            self._weekly_id = cid
            self.weekly_title = title
            self.weekly_desc = desc
            self.weekly_target = target
            self.weekly_progress = app.challenges_repo.get_progress(cid)
            self._recompute_progress()

        # Carrusel de fotos a partir de assets/images
        images_dir = Path("assets/images")
        exts = {".jpg", ".jpeg", ".png", ".webp"}
        image_paths = [
            str(p.as_posix())
            for p in sorted(images_dir.iterdir())
            if p.suffix.lower() in exts and "logo" not in p.name.lower()
        ] if images_dir.exists() else []

        carousel: Carousel = self.ids.get("photos_carousel")
        if carousel is not None:
            carousel.clear_widgets()
            # Optionally, pair images with tip texts
            tips = App.get_running_app().tips_repo.featured(limit=len(image_paths))
            for idx, img_path in enumerate(image_paths):
                title = tips[idx][1] if idx < len(tips) else ""
                body = tips[idx][2] if idx < len(tips) else ""

                root = FloatLayout()
                if img_path and exists(img_path):
                    bg = FitImage(source=img_path, allow_stretch=True, keep_ratio=False)
                    bg.size_hint = (1, 1)
                    root.add_widget(bg)

                overlay = MDBoxLayout(orientation="vertical", padding="16dp", spacing="6dp")
                # Overlay pegado abajo y ocupando TODO el ancho del slide
                overlay.size_hint = (1, None)
                overlay.height = 120
                overlay.pos_hint = {"x": 0, "y": 0}
                with overlay.canvas.before:
                    Color(0, 0, 0, 0.35)
                    rect = Rectangle(pos=(0, 0), size=(0, 0))

                # Captura temprana del rect/overlay para evitar late-binding
                def _sync_rect(_instance, _value, r=rect, ov=overlay):
                    r.pos = ov.pos
                    r.size = ov.size

                overlay.bind(pos=_sync_rect, size=_sync_rect)
                # Inicializa inmediatamente para este slide
                _sync_rect(None, None)

                if title:
                    t_lbl = MDLabel(text=title)
                    t_lbl.text_color = (1, 1, 1, 1)
                    t_lbl.font_size = sp(22)
                    t_lbl.size_hint_y = None
                    t_lbl.halign = "left"
                    t_lbl.text_size = (lambda: (overlay.width - 32, None))()
                    t_lbl.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1]))
                    overlay.bind(width=lambda *_: setattr(t_lbl, 'text_size', (overlay.width - 32, None)))
                    overlay.add_widget(t_lbl)
                if body:
                    b_lbl = MDLabel(text=body)
                    b_lbl.text_color = (1, 1, 1, 1)
                    b_lbl.font_size = sp(16)
                    b_lbl.size_hint_y = None
                    b_lbl.halign = "left"
                    b_lbl.text_size = (lambda: (overlay.width - 32, None))()
                    b_lbl.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1]))
                    overlay.bind(width=lambda *_: setattr(b_lbl, 'text_size', (overlay.width - 32, None)))
                    overlay.add_widget(b_lbl)

                root.add_widget(overlay)
                carousel.add_widget(root)

            # Auto-desplazamiento si hay más de 1 slide
            if len(image_paths) > 1:
                # Evita múltiples timers si se recarga la pantalla
                if hasattr(self, "_carousel_ev") and self._carousel_ev is not None:
                    self._carousel_ev.cancel()
                self._carousel_ev = Clock.schedule_interval(lambda dt: carousel.load_next(), 5.0)

        # Reflect progress in UI
        self._update_ui_progress()

    # Called from kv
    def register_recycling(self):
        if not self._weekly_id:
            return
        app = App.get_running_app()
        self.weekly_progress = app.challenges_repo.increment_progress(self._weekly_id, 1)
        self._recompute_progress()
        self._update_ui_progress()

    def _recompute_progress(self) -> None:
        target = max(1, int(self.weekly_target))
        progress = int(self.weekly_progress)
        self.progress_percent = min(100.0, (progress / target) * 100.0)
        self.progress_text = f"{progress}/{target}"

    def _update_ui_progress(self) -> None:
        ids = getattr(self, 'ids', {})
        bar = ids.get('weekly_progress')
        label = ids.get('weekly_progress_label')
        if bar is not None:
            bar.value = self.progress_percent
        if label is not None:
            label.text = self.progress_text
