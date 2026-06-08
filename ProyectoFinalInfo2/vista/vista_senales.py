import os
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class VistaSenales(QWidget):

    def __init__(self):
        super().__init__()
        ruta_ui = os.path.join(os.path.dirname(__file__), 'ui', 'modulo_senales.ui')
        uic.loadUi(ruta_ui, self)

        self.figura = Figure(figsize=(10, 5), dpi=100)
        self.canvas = FigureCanvas(self.figura)
        self.canvas.setMinimumHeight(350)

        layout = self.contenedor_canvas.layout()
        if layout is None:
            layout = QVBoxLayout(self.contenedor_canvas)
        layout.addWidget(self.canvas)

    def limpiar_canvas(self):
        self.figura.clear()
        self.canvas.draw()

    def dibujar_canales_seleccionados(self, datos, canales):
        self.figura.clear()
        ax = self.figura.add_subplot(111)
        colores = ['#2196F3', '#FF5722', '#4CAF50', '#FFC107',
                   '#9C27B0', '#00BCD4', '#E91E63', '#795548']
        for i, canal in enumerate(canales):
            ax.plot(datos[i, :], color=colores[i % len(colores)],
                    linewidth=0.8, label='Canal ' + str(canal))
        ax.set_title("Canales Seleccionados")
        ax.set_xlabel("Muestras")
        ax.set_ylabel("Amplitud")
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        self.figura.tight_layout()
        self.canvas.draw()

    def dibujar_comparacion_ruido(self, original, ruido, nombre_canal):
        self.figura.clear()
        ax1 = self.figura.add_subplot(211)
        ax2 = self.figura.add_subplot(212)

        ax1.plot(original, color='#2196F3', linewidth=0.8)
        ax1.set_title("Canal " + str(nombre_canal) + " - Original")
        ax1.grid(True, alpha=0.3)

        ax2.plot(ruido, color='#FF5722', linewidth=0.8)
        ax2.set_title("Canal " + str(nombre_canal) + " - Con Ruido")
        ax2.set_xlabel("Muestras")
        ax2.grid(True, alpha=0.3)

        self.figura.tight_layout()
        self.canvas.draw()

    def dibujar_promedio_std(self, promedio, desviacion, eje_texto):
        self.figura.clear()
        ax1 = self.figura.add_subplot(211)
        ax2 = self.figura.add_subplot(212)

        x = np.arange(len(promedio))
        ax1.stem(x, promedio, linefmt='g-', markerfmt='go', basefmt=' ')
        ax1.set_title("Promedio - " + eje_texto)
        ax1.set_ylabel("Valor")
        ax1.grid(True, alpha=0.3)

        ax2.stem(x, desviacion, linefmt='r-', markerfmt='ro', basefmt=' ')
        ax2.set_title("Desviacion Estandar - " + eje_texto)
        ax2.set_xlabel("Indice")
        ax2.set_ylabel("Valor")
        ax2.grid(True, alpha=0.3)

        self.figura.tight_layout()
        self.canvas.draw()

    def mostrar_info(self, texto):
        if hasattr(self, 'lbl_info_senal'):
            self.lbl_info_senal.setText(texto)

    def actualizar_spinbox_canales(self, max_canales):
        if hasattr(self, 'spin_canal_inicio'):
            self.spin_canal_inicio.setMaximum(max_canales - 1)
        if hasattr(self, 'spin_canal_fin'):
            self.spin_canal_fin.setMaximum(max_canales - 1)
        if hasattr(self, 'spin_canal_ruido'):
            self.spin_canal_ruido.setMaximum(max_canales - 1)