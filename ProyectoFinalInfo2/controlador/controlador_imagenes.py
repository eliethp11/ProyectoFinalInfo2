from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from modelo.modelo_procesamiento_imagenes import ProcesadorImagenesMedicasModelo
import os
import numpy as np
import pandas as pd
import cv2


CARPETA_EXPORTACION = "datos"

class ImagenesController:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = ProcesadorImagenesMedicasModelo()

        if self.vista.btn_cargar_imagen:
            self.vista.btn_cargar_imagen.clicked.connect(self.cargar_archivo)

        if self.vista.btn_guardardatos:
            self.vista.btn_guardardatos.clicked.connect(self.guardar_datos_csv)

        for sld in [self.vista.sld_axial, self.vista.sld_coronal, self.vista.sld_sagital]:
            if sld: 
                sld.valueChanged.connect(self.actualizar_cortes)

        self.inicializar_controles_opencv()
     
    def inicializar_controles_opencv(self):
        if self.vista.cb_filtro_tipo:
            self.vista.cb_filtro_tipo.clear()
            self.vista.cb_filtro_tipo.addItems(["Ninguno", "Desenfoque Gausiano", "Median Blur", "Bilateral"])
            self.vista.cb_filtro_tipo.addItems(["Ninguno", "Desenfoque Gausiano", "Median Blur", "Bilateral"])
        
        if self.vista.cb_umbral_tipo:
            self.vista.cb_umbral_tipo.clear()
            self.vista.cb_umbral_tipo.addItems(["Ninguno", "Umbral Binario", "Umbral Adaptativo"])
            self.vista.cb_umbral_tipo.currentIndexChanged.connect(self.aplicar_procesamiento)

        if self.vista.cb_morfologia:
            self.vista.cb_morfologia.clear()
            self.vista.cb_morfologia.addItems(["Ninguna", "Erosión", "Dilatación", "Apertura", "Cierre"])
            self.vista.cb_morfologia.currentIndexChanged.connect(self.aplicar_procesamiento)

        if self.vista.sld_intensidad_filtro:
            self.vista.sld_intensidad_filtro.setRange(1, 20)
            self.vista.sld_intensidad_filtro.setValue(5)
            self.vista.sld_intensidad_filtro.sliderReleased.connect(self.aplicar_procesamiento)

        if self.vista.sld_umbral_manual:
            self.vista.sld_umbral_manual.setRange(0, 255)
            self.vista.sld_umbral_manual.setValue(127)
            self.vista.sld_umbral_manual.sliderReleased.connect(self.aplicar_procesamiento)

        if self.vista.sld_morfologia_it:
            self.vista.sld_morfologia_it.setRange(1, 10)
            self.vista.sld_morfologia_it.setValue(1)
            self.vista.sld_morfologia_it.sliderReleased.connect(self.aplicar_procesamiento)

        if self.vista.btn_reset_opencv:
            self.vista.btn_reset_opencv.clicked.connect(self.reset_filtros)

        if self.vista.btn_canny_bordes:
            self.vista.btn_canny_bordes.clicked.connect(self.detectar_bordes)

        if self.vista.btn_exportar_procesada:
            self.vista.btn_exportar_procesada.clicked.connect(self.exportar_imagen)

    def cargar_archivo(self):
        self.vista.mostrar_mensaje_guardado("")

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("¿Qué tipo de recurso desea cargar?")
        msg.setWindowTitle("Selección de recurso")
        btn_archivo = msg.addButton("Archivo", QMessageBox.YesRole)
        btn_carpeta = msg.addButton("Carpeta (Serie DICOM)", QMessageBox.NoRole)
        msg.exec_()

        ruta = None
        if msg.clickedButton() == btn_archivo:
            ruta, _ = QFileDialog.getOpenFileName(None, "Cargar", "", "Médicas (*.dcm *.nii *.nii.gz);;Estándar (*.jpg *.png *.jpeg)")
        elif msg.clickedButton() == btn_carpeta:
            ruta = QFileDialog.getExistingDirectory(None, "Seleccionar Carpeta")

        if not ruta: return
        if self.modelo.cargar_y_procesar(ruta):
            if self.modelo.tipo_archivo == "OPENCV":
                if self.vista.stacked_procesamiento:
                    self.vista.stacked_procesamiento.setCurrentIndex(1) 
                self.actualizar_vista_opencv()
            else:
                if self.vista.stacked_procesamiento:
                    self.vista.stacked_procesamiento.setCurrentIndex(0) 
                z, y, x = self.modelo.shape
                self.vista.sld_axial.setMaximum(z - 1)
                self.vista.sld_coronal.setMaximum(y - 1)
                self.vista.sld_sagital.setMaximum(x - 1)
                self.actualizar_cortes()

            self.vista.mostrar_metadatos(self.modelo.metadata)

    def aplicar_procesamiento(self):
        if self.modelo.img_original is None: return
        img = self.modelo.img_original.copy()

        filtro = self.vista.cb_filtro_tipo.currentText()
        k = self.vista.sld_intensidad_filtro.value()
        if k % 2 == 0: k += 1

        if filtro == "Desenfoque Gausiano": img = cv2.GaussianBlur(img, (k, k), 0)
        elif filtro == "Median Blur": img = cv2.medianBlur(img, k)
        elif filtro == "Bilateral": img = cv2.bilateralFilter(img, 9, 75, 75)

        umbral_tipo = self.vista.cb_umbral_tipo.currentText()
        thresh_val = self.vista.sld_umbral_manual.value()

        if umbral_tipo != "Ninguno":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            if umbral_tipo == "Binario Simple": _, img = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
            elif umbral_tipo == "Binario Invertido": _, img = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
            elif umbral_tipo == "Otsu": _, img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            elif umbral_tipo == "Adaptativo": img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        morfo = self.vista.cb_morfologia.currentText()
        its = self.vista.sld_morfologia_it.value()
        kernel = np.ones((3,3), np.uint8)

        if morfo == "Erosión": img = cv2.erode(img, kernel, iterations=its)
        elif morfo == "Dilatación": img = cv2.dilate(img, kernel, iterations=its)
        elif morfo == "Apertura": img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        elif morfo == "Cierre": img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

        self.modelo.img_procesada = img
        self.actualizar_vista_opencv()

    def detectar_bordes(self):
        if self.modelo.img_original is None: return
        gray = cv2.cvtColor(self.modelo.img_original, cv2.COLOR_BGR2GRAY) if len(self.modelo.img_original.shape) == 3 else self.modelo.img_original
        self.modelo.img_procesada = cv2.Canny(gray, 50, 150)
        self.actualizar_vista_opencv()

    def reset_filtros(self):
        if self.modelo.img_original is not None:
            self.modelo.img_procesada = self.modelo.img_original.copy()
            self.vista.cb_filtro_tipo.setCurrentIndex(0)
            self.vista.cb_umbral_tipo.setCurrentIndex(0)
            self.vista.cb_morfologia.setCurrentIndex(0)
            self.actualizar_vista_opencv()

    def actualizar_vista_opencv(self):
        if self.modelo.img_original is not None:
            self.vista.mostrar_slice(self.modelo.img_original, self.vista.lbl_img_original)
            self.vista.mostrar_slice(self.modelo.img_procesada, self.vista.lbl_img_procesada)

    def exportar_imagen(self):
        if self.modelo.img_procesada is None: return
        ruta, _ = QFileDialog.getSaveFileName(None, "Guardar", "procesada.png", "PNG (*.png)")
        if ruta: cv2.imwrite(ruta, self.modelo.img_procesada)

    def guardar_datos_csv(self):
        metadata = self.modelo.obtener_metadata_para_csv()
        if not metadata: return
        nombre_archivo, ok = QInputDialog.getText(None, 'Guardar', 'Ingrese nombre:')
        if ok and nombre_archivo:
            df = pd.DataFrame(metadata.items(), columns=['Etiqueta', 'Valor'])
            if not os.path.exists(CARPETA_EXPORTACION): os.makedirs(CARPETA_EXPORTACION)
            df.to_csv(os.path.join(CARPETA_EXPORTACION, f"{nombre_archivo}.csv"), index=False)
        self.vista.mostrar_mensaje_guardado("Metadata guardada en " + CARPETA_EXPORTACION)

    def actualizar_cortes(self):
        if self.modelo.volumen is None: return
        z = self.vista.sld_axial.value()
        y = self.vista.sld_coronal.value()
        x = self.vista.sld_sagital.value()
        self.vista.mostrar_slice(self.modelo.obtener_corte_axial(z), self.vista.lbl_axial)
        self.vista.mostrar_slice(self.modelo.obtener_corte_coronal(y), self.vista.lbl_coronal)
        self.vista.mostrar_slice(np.rot90(self.modelo.obtener_corte_sagital(x), k=3), self.vista.lbl_sagital)
