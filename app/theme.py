from typing import Any
from kivy.core.window import Window


def setup_theme(app: Any) -> None:
    """Configure base theme for the application.

    Keep this minimal for MVP; later we can register custom fonts and roles.
    """
    app.theme_cls.theme_style = "Light"
    app.theme_cls.primary_palette = "Green"
    app.theme_cls.primary_hue = "600"
    # Ensure window background is light and not black
    Window.clearcolor = (1, 1, 1, 1)


