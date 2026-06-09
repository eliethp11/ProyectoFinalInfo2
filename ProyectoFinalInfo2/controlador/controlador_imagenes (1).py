import os
from PySide6.QtCore import QObject, Slot
import numpy as np
class ControladorImagenes(QObject):
    def __init__(self, modelo_dicom, modelo_nifti, vista):
        super().__init__()
        self.modelo_dicom = modelo_dicom
        self.modelo_nifti = modelo_nifti
        self.vista = vista
        self.slice_idx_axial = 0
        self.slice_idx_coronal = 0
        self.slice_idx_sagittal = 0
        
        self.wc_actual = 40       
        self.ww_actual = 400      
        self.zoom_actual = 1.0
        self.crop_activo = None
        self._conectar_eventos()
        self._deshabilitar_controles_iniciales()
    def _conectar_eventos(self):

        ui = self.vista.ui
        ui.btn_load_dicom_file.clicked.connect(self.cargar_dicom_individual)
        ui.btn_load_dicom_dir.clicked.connect(self.cargar_serie_dicom)
        ui.btn_load_nifti.clicked.connect(self.cargar_nifti)
        ui.btn_convert_nifti.clicked.connect(self.convertir_a_nifti)
        ui.btn_export_csv.clicked.connect(self.exportar_csv)
        ui.slider_axial.valueChanged.connect(self.cambiar_corte_axial)
        ui.slider_coronal.valueChanged.connect(self.cambiar_corte_coronal)
        ui.slider_sagittal.valueChanged.connect(self.cambiar_corte_sagittal)
        ui.slider_wc.valueChanged.connect(self.cambiar_window_center)
        ui.slider_ww.valueChanged.connect(self.cambiar_window_width)
        ui.btn_preset_brain.clicked.connect(lambda: self.aplicar_preset_ventana(40, 80))
        ui.btn_preset_lung.clicked.connect(lambda: self.aplicar_preset_ventana(-600, 1500))
        ui.btn_preset_bone.clicked.connect(lambda: self.aplicar_preset_ventana(480, 2500))
        ui.slider_zoom.valueChanged.connect(self.cambiar_zoom)
        ui.btn_apply_crop.clicked.connect(self.aplicar_recorte)
        ui.btn_reset_crop.clicked.connect(self.restablecer_recorte)
        ui.check_show_segmentation.stateChanged.connect(self.actualizar_vistas_2d)
        ui.slider_tmin.valueChanged.connect(self.cambiar_umbral_segmentacion)
        ui.slider_tmax.valueChanged.connect(self.cambiar_umbral_segmentacion)
        ui.btn_apply_morphology.clicked.connect(self.aplicar_morfologia)
        ui.btn_reconstruct_3d.clicked.connect(self.reconstruir_3d)
    def _deshabilitar_controles_iniciales(self):

        ui = self.vista.ui
        ui.tabWidget_controls.setTabEnabled(1, False) # Ajustes Visuales
        ui.tabWidget_controls.setTabEnabled(2, False) # Segmentación
        ui.btn_convert_nifti.setEnabled(False)
        ui.btn_export_csv.setEnabled(False)
    def _habilitar_controles(self):

        ui = self.vista.ui
        ui.tabWidget_controls.setTabEnabled(1, True)
        ui.tabWidget_controls.setTabEnabled(2, True)
        ui.btn_convert_nifti.setEnabled(True)
        ui.btn_export_csv.setEnabled(True)
    @Slot()
    def cargar_dicom_individual(self):
        file_path = self.vista.seleccionar_archivo_dicom()
        if not file_path:
            return
        
        try:
            self.modelo_dicom.cargar_archivo_individual(file_path)
            self._inicializar_interfaz_con_volumen()
            self.vista.mostrar_mensaje("Éxito", "Archivo DICOM cargado correctamente.")
        except Exception as e:
            self.vista.mostrar_error("Error de Carga", str(e))
    @Slot()
    def cargar_serie_dicom(self):
        dir_path = self.vista.seleccionar_directorio_dicom()
        if not dir_path:
            return
        
        try:
            self.modelo_dicom.cargar_serie_directorio(dir_path)
            self._inicializar_interfaz_con_volumen()
            self.vista.mostrar_mensaje("Éxito", f"Serie DICOM cargada con {len(self.modelo_dicom.slices)} cortes.")
        except Exception as e:
            self.vista.mostrar_error("Error de Carga", str(e))
    @Slot()
    def cargar_nifti(self):
        file_path = self.vista.seleccionar_archivo_nifti()
        if not file_path:
            return
        
        try:
            vol, spacing = self.modelo_nifti.cargar_nifti(file_path)
            
            self.modelo_dicom.volume_hu = vol
            self.modelo_dicom.volume_raw = vol 
            self.modelo_dicom.spacing = spacing
            self.modelo_dicom.slices = [None] * vol.shape[0] 
            
            z_size, y_size, x_size = vol.shape
            self.modelo_dicom.crop_limits = {
                'z_min': 0, 'z_max': z_size - 1,
                'y_min': 0, 'y_max': y_size - 1,
                'x_min': 0, 'x_max': x_size - 1
            }
            self.modelo_dicom.segmentation_mask = self.modelo_dicom.segmentation_mask = np.zeros_like(vol, dtype=bool)
            
            self.modelo_dicom.metadata = {
                'PatientName': {'value': 'NIfTI_FILE', 'label': 'Nombre Paciente'},
                'PatientID': {'value': 'N/A', 'label': 'ID Paciente'},
                'Modality': {'value': 'NIfTI', 'label': 'Modalidad'},
                'SliceThickness': {'value': float(spacing[0]), 'label': 'Espesor de Corte (mm)'},
                'PixelSpacing': {'value': f"[{spacing[1]:.2f}, {spacing[2]:.2f}]", 'label': 'Espaciado Píxeles (mm)'}
            }
            
            self._inicializar_interfaz_con_volumen()
            self.vista.mostrar_mensaje("Éxito", f"Volumen NIfTI ({z_size}x{y_size}x{x_size}) cargado correctamente.")
        except Exception as e:
            self.vista.mostrar_error("Error de Carga NIfTI", str(e))
    def _inicializar_interfaz_con_volumen(self):
  
        vol = self.modelo_dicom.volume_hu
        z_size, y_size, x_size = vol.shape
        ui = self.vista.ui
        ui.slider_axial.setMinimum(0)
        ui.slider_axial.setMaximum(z_size - 1)
        ui.slider_coronal.setMinimum(0)
        ui.slider_coronal.setMaximum(y_size - 1)
        ui.slider_sagittal.setMinimum(0)
        ui.slider_sagittal.setMaximum(x_size - 1)
        self.slice_idx_axial = z_size // 2
        self.slice_idx_coronal = y_size // 2
        self.slice_idx_sagittal = x_size // 2
        ui.slider_axial.setValue(self.slice_idx_axial)
        ui.slider_coronal.setValue(self.slice_idx_coronal)
        ui.slider_sagittal.setValue(self.slice_idx_sagittal)
        ui.slider_wc.setMinimum(-1024)
        ui.slider_wc.setMaximum(1500)
        ui.slider_wc.setValue(self.wc_actual)
        ui.lbl_wc_val.setText(str(self.wc_actual))
        ui.slider_ww.setMinimum(1)
        ui.slider_ww.setMaximum(3000)
        ui.slider_ww.setValue(self.ww_actual)
        ui.lbl_ww_val.setText(str(self.ww_actual))
        ui.spin_ymin.setRange(0, y_size - 2)
        ui.spin_ymin.setValue(0)
        ui.spin_ymax.setRange(1, y_size)
        ui.spin_ymax.setValue(y_size)
        ui.spin_xmin.setRange(0, x_size - 2)
        ui.spin_xmin.setValue(0)
        ui.spin_xmax.setRange(1, x_size)
        ui.spin_xmax.setValue(x_size)
        ui.slider_tmin.setMinimum(-1024)
        ui.slider_tmin.setMaximum(1500)
        ui.slider_tmin.setValue(200)
        ui.lbl_tmin_val.setText("200")
        ui.slider_tmax.setMinimum(-1024)
        ui.slider_tmax.setMaximum(1500)
        ui.slider_tmax.setValue(1000)
        ui.lbl_tmax_val.setText("1000")
        meta = self.modelo_dicom.metadata
        nombre = meta.get('PatientName', {}).get('value', 'N/A')
        paciente_id = meta.get('PatientID', {}).get('value', 'N/A')
        estudio = meta.get('StudyDescription', {}).get('value', 'N/A')
        modalidad = meta.get('Modality', {}).get('value', 'N/A')
        
        self.vista.actualizar_cabecera_paciente(nombre, paciente_id, estudio, modalidad)
        tabla_datos = self.modelo_dicom.obtener_tabla_metadatos()
        self.vista.popular_tabla_metadatos(tabla_datos)
        self._habilitar_controles()
        self.actualizar_vistas_2d()
        
        self.vista.renderizar_malla_3d(None, None)
    @Slot(int)
    def cambiar_corte_axial(self, valor):
        self.slice_idx_axial = valor
        self.actualizar_vistas_2d()
    @Slot(int)
    def cambiar_corte_coronal(self, valor):
        self.slice_idx_coronal = valor
        self.actualizar_vistas_2d()
    @Slot(int)
    def cambiar_corte_sagittal(self, valor):
        self.slice_idx_sagittal = valor
        self.actualizar_vistas_2d()
    @Slot(int)
    def cambiar_window_center(self, valor):
        self.wc_actual = valor
        self.vista.ui.lbl_wc_val.setText(str(valor))
        self.actualizar_vistas_2d()
    @Slot(int)
    def cambiar_window_width(self, valor):
        self.ww_actual = valor
        self.vista.ui.lbl_ww_val.setText(str(valor))
        self.actualizar_vistas_2d()
    def aplicar_preset_ventana(self, wc, ww):

        self.wc_actual = wc
        self.ww_actual = ww
        self.vista.ui.slider_wc.setValue(wc)
        self.vista.ui.slider_ww.setValue(ww)
        self.vista.ui.lbl_wc_val.setText(str(wc))
        self.vista.ui.lbl_ww_val.setText(str(ww))
        self.actualizar_vistas_2d()
    @Slot(int)
    def cambiar_zoom(self, valor):
        self.zoom_actual = valor / 100.0
        self.vista.ui.lbl_zoom_val.setText(f"{self.zoom_actual:.2f}x")
        self.actualizar_vistas_2d()
    @Slot()
    def aplicar_recorte(self):
        ui = self.vista.ui
        ymin = ui.spin_ymin.value()
        ymax = ui.spin_ymax.value()
        xmin = ui.spin_xmin.value()
        xmax = ui.spin_xmax.value()
        if ymin >= ymax or xmin >= xmax:
            self.vista.mostrar_error("Error de Recorte", "Los valores Mínimos deben ser menores a los Máximos.")
            return
        self.crop_activo = (ymin, ymax, xmin, xmax)
        self.actualizar_vistas_2d()
    @Slot()
    def restablecer_recorte(self):
        self.crop_activo = None
        
        self.zoom_actual = 1.0
        self.vista.ui.slider_zoom.setValue(100)
        self.vista.ui.lbl_zoom_val.setText("1.00x")
        
        vol = self.modelo_dicom.volume_hu
        if vol is not None:
            z, y, x = vol.shape
            self.vista.ui.spin_ymin.setValue(0)
            self.vista.ui.spin_ymax.setValue(y)
            self.vista.ui.spin_xmin.setValue(0)
            self.vista.ui.spin_xmax.setValue(x)
            
        self.actualizar_vistas_2d()
    @Slot()
    def cambiar_umbral_segmentacion(self):
        ui = self.vista.ui
        tmin = ui.slider_tmin.value()
        tmax = ui.slider_tmax.value()
        if tmin > tmax:
            tmax = tmin
            ui.slider_tmax.setValue(tmax)
            
        ui.lbl_tmin_val.setText(str(tmin))
        ui.lbl_tmax_val.setText(str(tmax))
        self.modelo_dicom.segmentar_por_umbral(tmin, tmax)
        
        if ui.check_show_segmentation.isChecked():
            self.actualizar_vistas_2d()
    @Slot()
    def aplicar_morfologia(self):
        ui = self.vista.ui
        operacion_esp = ui.combo_morphology.currentText()
        radio = ui.spin_kernel_size.value()
        op_map = {
            "Erosión": "erosion",
            "Dilatación": "dilatacion",
            "Apertura": "apertura",
            "Cierre": "cierre"
        }
        op_key = op_map.get(operacion_esp)
        
        try:
            tmin = ui.slider_tmin.value()
            tmax = ui.slider_tmax.value()
            self.modelo_dicom.segmentar_por_umbral(tmin, tmax)
            
            self.modelo_dicom.aplicar_operacion_morfologica(op_key, radio)
            
            self.vista.mostrar_mensaje("Morfología", f"Operación '{operacion_esp}' de radio {radio} aplicada en 3D.")
            
            if ui.check_show_segmentation.isChecked():
                self.actualizar_vistas_2d()
        except Exception as e:
            self.vista.mostrar_error("Error Morfológico", str(e))
    @Slot()
    def reconstruir_3d(self):
        ui = self.vista.ui
        step = ui.spin_step_size.value()
        try:
            tmin = ui.slider_tmin.value()
            tmax = ui.slider_tmax.value()
            
            if self.modelo_dicom.segmentation_mask is None or not self.modelo_dicom.segmentation_mask.any():
                self.modelo_dicom.segmentar_por_umbral(tmin, tmax)
            ui.tabWidget_visualizers.setCurrentIndex(1)
            
            vertices, caras = self.modelo_dicom.generar_malla_3d(paso=step)
            
            if vertices is None or len(vertices) == 0:
                self.vista.mostrar_mensaje("Reconstrucción 3D", "La máscara de segmentación está vacía. Ajuste los umbrales de HU.")
                return
            self.vista.renderizar_malla_3d(vertices, caras)
            
        except Exception as e:
            self.vista.mostrar_error("Error 3D", f"No se pudo completar la reconstrucción 3D: {e}")
    @Slot()
    def exportar_csv(self):
        file_path = self.vista.guardar_archivo_dialogo(
            "Exportar metadatos a CSV", "Archivos CSV (*.csv)"
        )
        if not file_path:
            return
            
        try:
            self.modelo_dicom.exportar_metadatos_csv(file_path)
            self.vista.mostrar_mensaje("Éxito", f"Metadatos guardados correctamente en:\n{file_path}")
        except Exception as e:
            self.vista.mostrar_error("Error al Exportar", str(e))
    @Slot()
    def convertir_a_nifti(self):
        file_path = self.vista.guardar_archivo_dialogo(
            "Exportar Serie a NIfTI", "Archivos NIfTI (*.nii.gz *.nii)"
        )
        if not file_path:
            return
            
        try:
            vol_hu = self.modelo_dicom.volume_hu
            spacing = self.modelo_dicom.spacing
            
            pos_inicial = None
            if self.modelo_dicom.slices and self.modelo_dicom.slices[0]:
                pos_inicial = getattr(self.modelo_dicom.slices[0], 'ImagePositionPatient', None)
            
            self.modelo_nifti.guardar_dicom_a_nifti(vol_hu, spacing, pos_inicial, file_path)
            self.vista.mostrar_mensaje("Éxito", f"Conversión completa. Archivo NIfTI guardado en:\n{file_path}")
        except Exception as e:
            self.vista.mostrar_error("Error de Conversión", str(e))
    @Slot()
    def actualizar_vistas_2d(self):

        if self.modelo_dicom.volume_hu is None:
            return
            
        ui = self.vista.ui
        mostrar_seg = ui.check_show_segmentation.isChecked()
        slice_ax = self.modelo_dicom.obtener_corte_visual(
            'axial', self.slice_idx_axial, self.wc_actual, self.ww_actual,
            zoom_factor=self.zoom_actual, crop_rect=self.crop_activo, mostrar_segmentacion=mostrar_seg
        )
        self.vista.renderizar_corte_2d('axial', slice_ax)
        ui.lbl_axial_idx.setText(f"Corte: {self.slice_idx_axial + 1}/{self.modelo_dicom.volume_hu.shape[0]}")
        slice_cor = self.modelo_dicom.obtener_corte_visual(
            'coronal', self.slice_idx_coronal, self.wc_actual, self.ww_actual,
            zoom_factor=self.zoom_actual, crop_rect=None, mostrar_segmentacion=mostrar_seg
        )
        self.vista.renderizar_corte_2d('coronal', slice_cor)
        ui.lbl_coronal_idx.setText(f"Corte: {self.slice_idx_coronal + 1}/{self.modelo_dicom.volume_hu.shape[1]}")
        slice_sag = self.modelo_dicom.obtener_corte_visual(
            'sagital', self.slice_idx_sagittal, self.wc_actual, self.ww_actual,
            zoom_factor=self.zoom_actual, crop_rect=None, mostrar_segmentacion=mostrar_seg
        )
        self.vista.renderizar_corte_2d('sagital', slice_sag)
        ui.lbl_sagittal_idx.setText(f"Corte: {self.slice_idx_sagittal + 1}/{self.modelo_dicom.volume_hu.shape[2]}")