import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow


class VistaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        ruta_ui = os.path.join(
            os.path.dirname(__file__),
            "ui",
            "ventana_principal.ui"
        )

        uic.loadUi(ruta_ui, self)
        self.setWindowTitle("Aplicativo Biomédico")