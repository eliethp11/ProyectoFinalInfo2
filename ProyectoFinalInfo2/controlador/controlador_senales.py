from PyQt5.QtWidgets import QFileDialog, QMessageBox
from modelo.modelo_senales import ModeloSenales
from vista.vista_senales import VistaSenales


class ControladorSenales:

    def __init__(self):
        self.modelo = ModeloSenales()
        self.vista = VistaSenales()
        self.vista.btn_cargar_mat.clicked.connect(self.cargar_archivo)
        self.vista.btn_mostrar_canales.clicked.connect(self.mostrar_canales)
        self.vista.btn_aplicar_ruido.clicked.connect(self.aplicar_ruido)
        self.vista.btn_comparar_ruido.clicked.connect(self.comparar_ruido)
        self.vista.btn_restaurar.clicked.connect(self.restaurar)
        self.vista.btn_calcular_estadisticas.clicked.connect(self.calcular_estadisticas)

    def cargar_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self.vista, "Seleccionar archivo .mat", "",
            "Archivos MATLAB (*.mat)"
        )
        if not ruta:
            return
        try:
            forma = self.modelo.cargar_archivo_mat(ruta)
            info = self.modelo.obtener_resumen_datos()
            texto = ("Forma: " + str(info['forma']) + "\n"
                     "Canales: " + str(info['canales']) + "\n"
                     "Tipo: " + info['tipo_datos'] + "\n"
                     "Rango: " + str(round(info['minimo'], 4)) +
                     " a " + str(round(info['maximo'], 4)))
            self.vista.mostrar_info(texto)
            self.vista.actualizar_spinbox_canales(info['canales'])
        except Exception as e:
            QMessageBox.critical(self.vista, "Error",
                                  "No se pudo cargar: " + str(e))

    def mostrar_canales(self):
        inicio = self.vista.spin_canal_inicio.value()
        fin = self.vista.spin_canal_fin.value()
        if inicio > fin:
            inicio, fin = fin, inicio

        canales = list(range(inicio, fin + 1))
        senal_2d = self.modelo.obtener_senal_2d()
        if senal_2d is None:
            QMessageBox.warning(self.vista, "Advertencia",
                                "Primero carga un archivo .mat")
            return

        datos = self.modelo.seleccionar_canales(senal_2d, canales)
        self.vista.dibujar_canales_seleccionados(datos, canales)

    def aplicar_ruido(self):
        canal = self.vista.spin_canal_ruido.value()
        tipo = self.vista.combo_tipo_ruido.currentText()
        nivel = self.vista.spin_nivel_ruido.value()

        resultado = self.modelo.agregar_ruido_canal(canal, tipo, nivel)
        if resultado[0] is None:
            QMessageBox.warning(self.vista, "Advertencia",
                                "Carga un archivo primero")
            return

        QMessageBox.information(self.vista, "Listo",
                                 "Ruido aplicado al canal " + str(canal))

    def comparar_ruido(self):
        canal = self.vista.spin_canal_ruido.value()
        original, modificada = self.modelo.obtener_comparacion_canal(canal)
        if original is None:
            QMessageBox.warning(self.vista, "Advertencia",
                                "Carga un archivo primero")
            return
        self.vista.dibujar_comparacion_ruido(original, modificada, canal)

    def restaurar(self):
        self.modelo.restaurar_senal_original()
        self.vista.limpiar_canvas()
        QMessageBox.information(self.vista, "Listo",
                                "Senal restaurada al original")

    def calcular_estadisticas(self):
        if self.modelo.datos_originales is None:
            QMessageBox.warning(self.vista, "Advertencia",
                                "Carga un archivo primero")
            return

        if self.vista.radio_eje_0.isChecked():
            eje = 0
        else:
            eje = 1

        promedio, desviacion = self.modelo.calcular_promedio_std_por_eje(eje)
        eje_texto = self.modelo.obtener_info_eje(eje)
        self.vista.dibujar_promedio_std(promedio, desviacion, eje_texto)

    def mostrar_vista(self):
        self.vista.show()