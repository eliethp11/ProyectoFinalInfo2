from PyQt5.QtWidgets import QMessageBox
from modelo.modelo_autenticacion import ModeloAutenticacion


class ControladorAutenticacion:
    def __init__(self, vista_login, controlador_principal):
        self.vista_login = vista_login
        self.controlador_principal = controlador_principal
        self.modelo_autenticacion = ModeloAutenticacion()

        self.conectar_eventos()

    def conectar_eventos(self):
        if hasattr(self.vista_login, "btn_ingresar"):
            self.vista_login.btn_ingresar.clicked.connect(self.validar_login)

    def validar_login(self):
        if not hasattr(self.vista_login, "txt_usuario") or not hasattr(self.vista_login, "txt_password"):
            QMessageBox.critical(
                self.vista_login,
                "Error de interfaz",
                "Faltan los objetos txt_usuario o txt_password en login.ui"
            )
            return

        nombre = self.vista_login.txt_usuario.text().strip()
        password = self.vista_login.txt_password.text().strip()

        if nombre == "" or password == "":
            QMessageBox.warning(
                self.vista_login,
                "Campos vacíos",
                "Debes ingresar usuario y contraseña."
            )
            return

        usuario = self.modelo_autenticacion.validar_usuario(nombre, password)

        if usuario:
            QMessageBox.information(
                self.vista_login,
                "Acceso permitido",
                f"Bienvenido, {usuario['nombre']} ({usuario['rol']})."
            )
            self.controlador_principal.login_exitoso(usuario)
        else:
            QMessageBox.warning(
                self.vista_login,
                "Acceso denegado",
                "Usuario o contraseña incorrectos."
            )