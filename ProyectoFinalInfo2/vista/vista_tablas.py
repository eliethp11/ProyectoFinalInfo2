import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow


class VistaTablas(QMainWindow):
    def __init__(self):
        super().__init__()

        ruta_ui = os.path.join(
            os.path.dirname(__file__),
            "ui",
            "modulo_tablas.ui"
        )

        uic.loadUi(ruta_ui, self)
        self.setWindowTitle("Módulo de Datos Tabulares")