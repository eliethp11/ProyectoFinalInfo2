import os
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog


class VistaLogin(QDialog):
    def __init__(self):
        super().__init__()

        ruta_ui = os.path.join(
            os.path.dirname(__file__),
            "ui",
            "login.ui"
        )

        uic.loadUi(ruta_ui, self)
        self.setWindowTitle("Inicio de sesión")