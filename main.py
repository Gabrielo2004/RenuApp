from kivy.core.window import Window
Window.size = (520, 790)
Window.resizable = False

from kivy.utils import platform
if platform == "win" or platform == "linux" or platform == "macosx":
    screen_w, screen_h = Window.system_size  # tamaño de la pantalla del usuario
    win_w, win_h = Window.size
    Window.left = int((screen_w - win_w) / 2)
    Window.top = int((screen_h - win_h) / 2)
    
from app.main import RenuApp

if __name__ == "__main__":
    RenuApp().run()
