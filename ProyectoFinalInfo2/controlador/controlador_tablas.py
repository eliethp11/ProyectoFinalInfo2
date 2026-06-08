import os
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QFileDialog,
    QListWidgetItem,
    QMessageBox,
    QTableWidgetItem
)

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

        columnas_describe = len(describe_df.columns) + 1 if not describe_df.empty else 3
        columnas_max = max(3, columnas_describe)

        total_filas = 0
        total_filas += 1
        total_filas += 1
        total_filas += len(info_df)
        total_filas += 1
        total_filas += 1
        total_filas += 1
        total_filas += len(describe_df)

        self.vista.tabla_resumen.setRowCount(total_filas)
        self.vista.tabla_resumen.setColumnCount(columnas_max)

        encabezados = ["Campo", "Valor 1", "Valor 2"]
        while len(encabezados) < columnas_max:
            encabezados.append(f"Valor {len(encabezados)}")

        self.vista.tabla_resumen.setHorizontalHeaderLabels(encabezados)

        fila = 0

        self.vista.tabla_resumen.setItem(fila, 0, QTableWidgetItem("INFO()"))
        fila += 1

        self.vista.tabla_resumen.setItem(fila, 0, QTableWidgetItem("columna"))
        self.vista.tabla_resumen.setItem(fila, 1, QTableWidgetItem("no_nulos"))
        self.vista.tabla_resumen.setItem(fila, 2, QTableWidgetItem("tipo_dato"))
        fila += 1

        for _, row in info_df.iterrows():
            self.vista.tabla_resumen.setItem(fila, 0, QTableWidgetItem(str(row["columna"])))
            self.vista.tabla_resumen.setItem(fila, 1, QTableWidgetItem(str(row["no_nulos"])))
            self.vista.tabla_resumen.setItem(fila, 2, QTableWidgetItem(str(row["tipo_dato"])))
            fila += 1

        self.vista.tabla_resumen.setItem(fila, 0, QTableWidgetItem(""))
        fila += 1

        self.vista.tabla_resumen.setItem(fila, 0, QTableWidgetItem("DESCRIBE()"))
        fila += 1

        headers_describe = ["estadistico"] + list(describe_df.columns)
        for j, nombre in enumerate(headers_describe):
            if j < columnas_max:
                self.vista.tabla_resumen.setItem(fila, j, QTableWidgetItem(nombre))
        fila += 1

        for _, row in describe_df.iterrows():
            self.vista.tabla_resumen.setItem(fila, 0, QTableWidgetItem(str(row.name)))
            for j, valor in enumerate(row.values, start=1):
                self.vista.tabla_resumen.setItem(fila, j, QTableWidgetItem(str(valor)))
            fila += 1

        self.vista.tabla_resumen.resizeColumnsToContents()

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
            df.plot(subplots=True, figsize=(8, 6), title=columnas)
            plt.tight_layout()
            plt.show()
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

            plt.figure(figsize=(6, 5))
            plt.scatter(x, y)
            plt.xlabel(columna_x)
            plt.ylabel(columna_y)
            plt.title(f"Scatter: {columna_x} vs {columna_y}")
            plt.tight_layout()
            plt.show()
        except Exception as e:
            QMessageBox.critical(self.vista, "Error", str(e))