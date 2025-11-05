from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class LoginScreen(MDScreen):
    def do_login(self):
        u = self.ids.username.text.strip()
        p = self.ids.password.text
        if not u or not p:
            self._show_msg("Ingresa usuario y contraseña")
            return
        app = App.get_running_app()
        user_id = app.users_repo.authenticate(u, p)
        if user_id:
            app.users_repo.set_current_user_id(user_id)
            app.set_logged_in(True)
            app.switch_to("home")
            self._show_msg("Bienvenido")
            return
        self._show_msg("Usuario o contraseña incorrectos")

    def goto_register(self):
        App.get_running_app().switch_to("register")

    def _show_msg(self, text: str) -> None:
        MDSnackbar(MDSnackbarText(text=text)).open()


class RegisterScreen(MDScreen):
    def do_register(self):
        u = self.ids.reg_username.text.strip()
        e = self.ids.reg_email.text.strip()
        p = self.ids.reg_password.text
        c = self.ids.reg_confirm.text
        if not u or not p or not c:
            self._show_msg("Completa usuario y contraseñas")
            return
        if len(p) < 6:
            self._show_msg("La contraseña debe tener al menos 6 caracteres")
            return
        if p != c:
            self._show_msg("Las contraseñas no coinciden")
            return
        app = App.get_running_app()
        try:
            app.users_repo.create_user(u, p, e or None)
            self._show_msg("Cuenta creada, inicia sesión")
            app.switch_to("login")
        except Exception as ex:
            self._show_msg(str(ex) or "No se pudo crear la cuenta")

    def go_back(self):
        App.get_running_app().switch_to("login")

    # Utilities
    def _show_msg(self, text: str) -> None:
        MDSnackbar(MDSnackbarText(text=text)).open()


