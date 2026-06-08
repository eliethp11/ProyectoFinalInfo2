import os
import numpy as np
from PyQt5.QtWidgets import (
    QFileDialog,
    QListWidgetItem,
    QMessageBox,
    QTableWidgetItem,
    QHeaderView,
    QMainWindow
)
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from vista.vista_tablas import VistaTablas
from modelo.modelo_tabular import ModeloTabular


class ControladorTablas:

    def __init__(self):
        self.vista = VistaTablas()
        self.modelo = ModeloTabular()
        self.conectar_eventos()

    def conectar_eventos(self):
        self.vista.btn_cargar_archivo.clicked.connect(self.cargar_archivo)
        self.vista.btn_graficar_columnas.clicked.connect(self.graficar_columnas)
        self.vista.btn_scatter.clicked.connect(self.graficar_scatter)

    def mostrar(self):
        self.vista.show()

    def cargar_archivo(self):
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self.vista,
            "Seleccionar archivo",
            "",
            "Archivos CSV o Excel (*.csv *.xlsx)"
        )

        if not ruta_archivo:
            return

        try:
            self.modelo.cargar_archivo(ruta_archivo)
            self.vista.lbl_archivo.setText(os.path.basename(ruta_archivo))
            self.cargar_lista_columnas()
            self.cargar_combos()
            self.mostrar_resumen_tabla()
        except Exception as e:
            QMessageBox.critical(self.vista, "Error", str(e))

    def cargar_lista_columnas(self):
        self.vista.lista_columnas.clear()
        columnas = self.modelo.obtener_columnas()

        for col in columnas:
            item = QListWidgetItem(col)
            self.vista.lista_columnas.addItem(item)

    def cargar_combos(self):
        columnas = self.modelo.obtener_columnas()
        self.vista.combo_x.clear()
        self.vista.combo_y.clear()
        self.vista.combo_x.addItems(columnas)
        self.vista.combo_y.addItems(columnas)

    def mostrar_resumen_tabla(self):
        info_df = self.modelo.obtener_info_dataframe()
        describe_df = self.modelo.obtener_describe()

        self.vista.tabla_resumen.clear()

        total_filas = 0
        encabezados_info = list(info_df.columns)
        total_filas += 1
        total_filas += 1
        total_filas += len(info_df)
        total_filas += 1
        total_filas += 1
        encabezados_desc = list(describe_df.columns)
        total_filas += 1
        total_filas += len(describe_df)

        columnas_max = max(len(encabezados_info), len(encabezados_desc), 3)
        self.vista.tabla_resumen.setRowCount(total_filas)
        self.vista.tabla_resumen.setColumnCount(columnas_max)

        encabezados_tabla = ["Campo"]
        for i in range(1, columnas_max):
            encabezados_tabla.append("Col " + str(i))
        self.vista.tabla_resumen.setHorizontalHeaderLabels(encabezados_tabla)

        fila = 0

        self.vista.tabla_resumen.setItem(fila, 0, QTableWidgetItem("INFO()"))
        for c in range(columnas_max):
            item = self.vista.tabla_resumen.item(fila, c)
            if item:
                item.setBackground(QColor("#1565C0"))
                item.setForeground(QColor("white"))
        fila += 1

        for j, nombre in enumerate(encabezados_info):
            self.vista.tabla_resumen.setItem(fila, j, QTableWidgetItem(nombre))
            item = self.vista.tabla_resumen.item(fila, j)
            if item:
                item.setBackground(QColor("#BBDEFB"))
                item.setForeground(QColor("#0D47A1"))
        fila += 1

        for _, row in info_df.iterrows():
            for j, nombre in enumerate(encabezados_info):
                valor = str(row[nombre]) if nombre in row else ""
                self.vista.tabla_resumen.setItem(fila, j, QTableWidgetItem(valor))
                item = self.vista.tabla_resumen.item(fila, j)
                if item:
                    item.setBackground(QColor("#E3F2FD"))
            fila += 1

        self.vista.tabla_resumen.setItem(fila, 0, QTableWidgetItem(""))
        fila += 1

        self.vista.tabla_resumen.setItem(fila, 0, QTableWidgetItem("DESCRIBE()"))
        for c in range(columnas_max):
            item = self.vista.tabla_resumen.item(fila, c)
            if item:
                item.setBackground(QColor("#2E7D32"))
                item.setForeground(QColor("white"))
        fila += 1

        for j, nombre in enumerate(encabezados_desc):
            self.vista.tabla_resumen.setItem(fila, j, QTableWidgetItem(nombre))
            item = self.vista.tabla_resumen.item(fila, j)
            if item:
                item.setBackground(QColor("#C8E6C9"))
                item.setForeground(QColor("#1B5E20"))
        fila += 1

        for _, row in describe_df.iterrows():
            self.vista.tabla_resumen.setItem(fila, 0, QTableWidgetItem(str(row.name)))
            for j, valor in enumerate(row.values, start=1):
                if j < columnas_max:
                    self.vista.tabla_resumen.setItem(fila, j, QTableWidgetItem(str(valor)))
                    item = self.vista.tabla_resumen.item(fila, j)
                    if item:
                        item.setBackground(QColor("#E8F5E9"))
            fila += 1

        header = self.vista.tabla_resumen.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

    def graficar_columnas(self):
        items = self.vista.lista_columnas.selectedItems()

        if len(items) < 1:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Selecciona al menos una columna."
            )
            return

        columnas = [item.text() for item in items]

        try:
            df = self.modelo.obtener_datos_columnas(columnas)

            fig = Figure(figsize=(8, 6))
            canvas = FigureCanvas(fig)
            axes = fig.subplots(len(columnas), 1, sharex=True)

            if len(columnas) == 1:
                axes = [axes]

            colores = ['#2196F3', '#FF5722', '#4CAF50', '#FFC107',
                       '#9C27B0', '#00BCD4', '#E91E63', '#795548']

            for i, col in enumerate(columnas):
                ax = axes[i]
                datos_col = df[col].dropna()
                ax.plot(datos_col.values, color=colores[i % len(colores)],
                        linewidth=0.8)
                ax.set_title(col)
                ax.grid(True, alpha=0.3)

            fig.tight_layout()

            ventana_grafica = QMainWindow()
            ventana_grafica.setWindowTitle("Grafico de Columnas")
            ventana_grafica.setCentralWidget(canvas)
            ventana_grafica.resize(800, 600)
            ventana_grafica.show()
        except Exception as e:
            QMessageBox.critical(self.vista, "Error", str(e))

    def graficar_scatter(self):
        columna_x = self.vista.combo_x.currentText()
        columna_y = self.vista.combo_y.currentText()

        if not columna_x or not columna_y:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Selecciona columnas para X y Y."
            )
            return

        try:
            x, y = self.modelo.obtener_datos_scatter(columna_x, columna_y)

            fig = Figure(figsize=(6, 5))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.scatter(x, y, alpha=0.5, color='#2196F3')
            ax.set_xlabel(columna_x)
            ax.set_ylabel(columna_y)
            ax.set_title(columna_x + " vs " + columna_y)
            ax.grid(True, alpha=0.3)
            fig.tight_layout()

            ventana_grafica = QMainWindow()
            ventana_grafica.setWindowTitle("Scatter Plot")
            ventana_grafica.setCentralWidget(canvas)
            ventana_grafica.resize(600, 500)
            ventana_grafica.show()
        except Exception as e:
            QMessageBox.critical(self.vista, "Error", str(e))