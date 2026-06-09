import os
import glob
import csv
import numpy as np
import pydicom
import scipy.ndimage as ndimage
import cv2
class ModeloDicom:
    def __init__(self):
        self.slices = []             
        self.volume_raw = None       
        self.volume_hu = None        
        self.spacing = (1.0, 1.0, 1.0)
        self.slice_thickness = 1.0
        
        self.metadata = {}
        
        self.segmentation_mask = None
        
        self.crop_limits = None
    def cargar_archivo_individual(self, filepath):

        try:
            ds = pydicom.dcmread(filepath)
            self.slices = [ds]
            
            self._inicializar_volumen()
            self._extraer_metadatos(ds)
            return True
        except Exception as e:
            print(f"Error al cargar archivo DICOM individual: {e}")
            raise IOError(f"El archivo DICOM está corrupto o es inválido: {e}")
    def cargar_serie_directorio(self, directory_path):

        try:
            files = []
            for ext in ('*.dcm', '*.DCM', '*'):
                files.extend(glob.glob(os.path.join(directory_path, ext)))
            
            dicom_files = []
            for f in files:
                if os.path.isdir(f):
                    continue
                try:
                    pydicom.read_preamble(f)  
                    dicom_files.append(f)
                except (pydicom.errors.InvalidDicomError, IOError):
                    try:
                        pydicom.dcmread(f, stop_before_pixels=True)
                        dicom_files.append(f)
                    except Exception:
                        continue
            
            if not dicom_files:
                raise FileNotFoundError("No se encontraron archivos DICOM válidos en el directorio.")
            
            loaded_slices = []
            for f in dicom_files:
                try:
                    ds = pydicom.dcmread(f)
                    if hasattr(ds, 'PixelData'):
                        loaded_slices.append(ds)
                except Exception as e:
                    print(f"Error cargando archivo {f}: {e}")
            
            if not loaded_slices:
                raise ValueError("Ninguno de los archivos DICOM contiene datos de píxeles legibles.")
            
            has_position = all(hasattr(s, 'ImagePositionPatient') and len(s.ImagePositionPatient) == 3 for s in loaded_slices)
            has_location = all(hasattr(s, 'SliceLocation') for s in loaded_slices)
            has_instance = all(hasattr(s, 'InstanceNumber') for s in loaded_slices)
            
            if has_position:
                loaded_slices.sort(key=lambda s: s.ImagePositionPatient[2])
            elif has_location:
                loaded_slices.sort(key=lambda s: s.SliceLocation)
            elif has_instance:
                def get_instance_num(s):
                    try:
                        return int(s.InstanceNumber)
                    except ValueError:
                        return 0
                loaded_slices.sort(key=get_instance_num)
            
            self.slices = loaded_slices
            self._inicializar_volumen()
            self._extraer_metadatos(self.slices[0])
            return True
            
        except Exception as e:
            print(f"Error al cargar serie DICOM del directorio: {e}")
            raise IOError(f"Error cargando la serie DICOM: {e}")
    def _inicializar_volumen(self):

        num_slices = len(self.slices)
        r, c = self.slices[0].Rows, self.slices[0].Columns
        
        self.volume_raw = np.zeros((num_slices, r, c), dtype=np.float32)
        for idx, ds in enumerate(self.slices):
            self.volume_raw[idx] = ds.pixel_array.astype(np.float32)
            
        self.volume_hu = np.zeros_like(self.volume_raw)
        for idx, ds in enumerate(self.slices):
            slope = float(getattr(ds, 'RescaleSlope', 1.0))
            intercept = float(getattr(ds, 'RescaleIntercept', 0.0))
            self.volume_hu[idx] = self.volume_raw[idx] * slope + intercept
            
        pixel_spacing = getattr(self.slices[0], 'PixelSpacing', [1.0, 1.0])
        dx = float(pixel_spacing[1])
        dy = float(pixel_spacing[0])
        
        dz = 1.0
        if num_slices > 1:
            if hasattr(self.slices[0], 'ImagePositionPatient') and hasattr(self.slices[1], 'ImagePositionPatient'):
                dz = abs(self.slices[1].ImagePositionPatient[2] - self.slices[0].ImagePositionPatient[2])
            elif hasattr(self.slices[0], 'SliceLocation') and hasattr(self.slices[1], 'SliceLocation'):
                dz = abs(self.slices[1].SliceLocation - self.slices[0].SliceLocation)
            else:
                dz = float(getattr(self.slices[0], 'SliceThickness', 1.0))
        else:
            dz = float(getattr(self.slices[0], 'SliceThickness', 1.0))
            
        self.spacing = (dz, dy, dx)
        self.slice_thickness = float(getattr(self.slices[0], 'SliceThickness', dz))
        
        self.segmentation_mask = np.zeros_like(self.volume_hu, dtype=bool)
        
        self.crop_limits = {
            'z_min': 0, 'z_max': num_slices - 1,
            'y_min': 0, 'y_max': r - 1,
            'x_min': 0, 'x_max': c - 1
        }
    def _extraer_metadatos(self, ds):

        tags = {
            'PatientName': ('Patient\'s Name', 'Nombre Paciente'),
            'PatientID': ('Patient ID', 'ID Paciente'),
            'PatientBirthDate': ('Patient\'s Birth Date', 'Fecha Nacimiento'),
            'PatientSex': ('Patient\'s Sex', 'Género'),
            'StudyDate': ('Study Date', 'Fecha Estudio'),
            'StudyTime': ('Study Time', 'Hora Estudio'),
            'Modality': ('Modality', 'Modalidad'),
            'Manufacturer': ('Manufacturer', 'Fabricante'),
            'InstitutionName': ('Institution Name', 'Institución'),
            'SliceThickness': ('Slice Thickness', 'Espesor de Corte (mm)'),
            'PixelSpacing': ('Pixel Spacing', 'Espaciado Píxeles (mm)'),
            'RescaleSlope': ('Rescale Slope', 'Rescale Slope'),
            'RescaleIntercept': ('Rescale Intercept', 'Rescale Intercept'),
            'WindowCenter': ('Window Center', 'Window Center (Nivel)'),
            'WindowWidth': ('Window Width', 'Window Width (Ancho)'),
        }
        
        self.metadata = {}
        for tag_name, (label_en, label_es) in tags.items():
            val = getattr(ds, tag_name, "N/A")
            
            if isinstance(val, pydicom.valuerep.DSfloat) or isinstance(val, pydicom.valuerep.DSdecimal):
                val = float(val)
            elif isinstance(val, pydicom.valuerep.IS):
                val = int(val)
            elif isinstance(val, pydicom.multival.MultiValue):
                val = [float(v) if isinstance(v, (pydicom.valuerep.DSfloat, pydicom.valuerep.DSdecimal)) else v for v in val]
                val = str(val)
            elif isinstance(val, pydicom.valuerep.PersonName):
                val = str(val)
                
            self.metadata[tag_name] = {
                'value': val,
                'label': label_es
            }
    def obtener_tabla_metadatos(self):

        data = []
        for tag_name, meta in self.metadata.items():
            try:
                tag_hex = str(pydicom.datadict.tag_for_keyword(tag_name))
            except Exception:
                tag_hex = "N/A"
            
            data.append({
                'tag': tag_hex,
                'description': meta['label'],
                'value': str(meta['value'])
            })
        return data
    def exportar_metadatos_csv(self, filepath):

        try:
            tabla = self.obtener_tabla_metadatos()
            with open(filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Tag DICOM', 'Descripción', 'Valor'])
                for item in tabla:
                    writer.writerow([item['tag'], item['description'], item['value']])
            return True
        except Exception as e:
            print(f"Error al exportar metadatos a CSV: {e}")
            raise IOError(f"No se pudo escribir el archivo CSV: {e}")
    def aplicar_windowing(self, slice_data, wc, ww):
 
        min_val = wc - (ww / 2.0)
        max_val = wc + (ww / 2.0)
        
        if ww <= 0:
            ww = 1.0
            
        output = (slice_data - min_val) / ww * 255.0
        output = np.clip(output, 0, 255).astype(np.uint8)
        return output
    def obtener_corte_2d(self, plano, indice):

        if self.volume_hu is None:
            return None
            
        z_size, y_size, x_size = self.volume_hu.shape
        
        if plano == 'axial':
            idx = np.clip(indice, 0, z_size - 1)
            return self.volume_hu[idx, :, :]
        elif plano == 'coronal':
            idx = np.clip(indice, 0, y_size - 1)
            return self.volume_hu[:, idx, :]
        elif plano == 'sagital':
            idx = np.clip(indice, 0, x_size - 1)
            return self.volume_hu[:, :, idx]
        else:
            raise ValueError(f"Plano anatómico '{plano}' no reconocido.")
    def obtener_corte_visual(self, plano, indice, wc, ww, zoom_factor=1.0, crop_rect=None, mostrar_segmentacion=False):

        corte = self.obtener_corte_2d(plano, indice)
        if corte is None:
            return None
            
        img_gray = self.aplicar_windowing(corte, wc, ww)
        
        if mostrar_segmentacion and self.segmentation_mask is not None:
            mask_2d = self.obtener_corte_segmentado_2d(plano, indice)
            
            img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
            
            tinte_rojo = np.zeros_like(img_color)
            tinte_rojo[mask_2d] = [255, 0, 0] # Rojo en RGB
            
            mask_indices = mask_2d > 0
            img_color[mask_indices] = cv2.addWeighted(img_color, 0.6, tinte_rojo, 0.4, 0)[mask_indices]
            img_final = img_color
        else:
            img_final = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
            
        if crop_rect is not None:
            ymin, ymax, xmin, xmax = crop_rect
            h, w = img_final.shape[:2]
            ymin = max(0, min(ymin, h - 1))
            ymax = max(ymin + 1, min(ymax, h))
            xmin = max(0, min(xmin, w - 1))
            xmax = max(xmin + 1, min(xmax, w))
            img_final = img_final[ymin:ymax, xmin:xmax]
            
        if zoom_factor != 1.0 and zoom_factor > 0.1:
            h, w = img_final.shape[:2]
            new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
            img_final = cv2.resize(img_final, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            
        return img_final
    def obtener_corte_segmentado_2d(self, plano, indice):
      
        if self.segmentation_mask is None:
            return None
            
        z_size, y_size, x_size = self.segmentation_mask.shape
        
        if plano == 'axial':
            idx = np.clip(indice, 0, z_size - 1)
            return self.segmentation_mask[idx, :, :]
        elif plano == 'coronal':
            idx = np.clip(indice, 0, y_size - 1)
            return self.segmentation_mask[:, idx, :]
        elif plano == 'sagital':
            idx = np.clip(indice, 0, x_size - 1)
            return self.segmentation_mask[:, :, idx]
        return None
    def segmentar_por_umbral(self, min_hu, max_hu):

        if self.volume_hu is None:
            return False
            
        self.segmentation_mask = (self.volume_hu >= min_hu) & (self.volume_hu <= max_hu)
        return True
    def aplicar_operacion_morfologica(self, operacion, radio_kernel):

        if self.segmentation_mask is None:
            return False
            
        struct = ndimage.generate_binary_structure(3, 1) # Vecindad de conectividad 1
        if radio_kernel > 1:
            struct = ndimage.iterate_structure(struct, int(radio_kernel))
            
        if operacion == 'erosion':
            self.segmentation_mask = ndimage.binary_erosion(self.segmentation_mask, structure=struct)
        elif operacion == 'dilatacion':
            self.segmentation_mask = ndimage.binary_dilation(self.segmentation_mask, structure=struct)
        elif operacion == 'apertura':
            self.segmentation_mask = ndimage.binary_opening(self.segmentation_mask, structure=struct)
        elif operacion == 'cierre':
            self.segmentation_mask = ndimage.binary_closing(self.segmentation_mask, structure=struct)
        else:
            raise ValueError(f"Operación morfológica '{operacion}' no válida.")
            
        return True
    def generar_malla_3d(self, paso=1):

        if self.segmentation_mask is None or not np.any(self.segmentation_mask):
            return None, None
            
        try:
            import skimage.measure as measure
            
            vol_binary = self.segmentation_mask.astype(np.uint8)
            
            verts, faces, normals, values = measure.marching_cubes(
                vol_binary, 
                level=0.5, 
                spacing=self.spacing, 
                step_size=paso
            )
            return verts, faces
        except ImportError:
            print("scikit-image no está disponible. Usando fallback de visualización por puntos.")
            indices = np.argwhere(self.segmentation_mask)
            vertices = indices * np.array(self.spacing)
            caras = np.array([])
            return vertices, caras
        except Exception as e:
            print(f"Error en la generación de malla 3D: {e}")
            return None, None