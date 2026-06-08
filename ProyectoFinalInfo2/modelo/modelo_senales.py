import numpy as np
import scipy.io


class ModeloSenales:

    def __init__(self):
        self.datos_originales = None
        self.nombre_variable = None
        self.forma_datos = None
        self.senal_trabajo = None
        self.num_canales = 0

    def cargar_archivo_mat(self, ruta_archivo):
        datos_mat = scipy.io.loadmat(ruta_archivo)
        claves_descartar = ['__header__', '__version__', '__globals__']
        for clave in datos_mat:
            if clave not in claves_descartar:
                self.nombre_variable = clave
                self.datos_originales = datos_mat[clave]
                break

        if self.datos_originales is None:
            raise ValueError("No se encontro variable de datos en el .mat")

        self.forma_datos = self.datos_originales.shape
        self.num_canales = self.forma_datos[0]
        self.senal_trabajo = self.datos_originales.copy()
        return self.forma_datos

    def obtener_senal_2d(self):
        if self.senal_trabajo is None:
            return None
        if self.senal_trabajo.ndim == 2:
            return self.senal_trabajo
        forma = self.senal_trabajo.shape
        return self.senal_trabajo.reshape((forma[0], -1))

    def seleccionar_canales(self, senal_2d, canales):
        return senal_2d[canales, :]

    def agregar_ruido_canal(self, canal_idx, tipo_ruido, nivel):
        senal_2d = self.obtener_senal_2d()
        if senal_2d is None:
            return None, None

        canal_original = senal_2d[canal_idx, :].copy()
        muestras = len(canal_original)
        ruido = np.zeros(muestras)

        if tipo_ruido == "Gaussiano":
            ruido = np.random.normal(0, nivel, muestras)
        elif tipo_ruido == "Impulso (Salt & Pepper)":
            prob = nivel / 100.0
            mascara = np.random.rand(muestras) < prob
            ruido[mascara] = canal_original.max() * 0.5
            mascara_min = np.random.rand(muestras) < prob * 0.5
            ruido[mascara_min] = -canal_original.max() * 0.5
        elif tipo_ruido == "Uniforme":
            ruido = np.random.uniform(-nivel, nivel, muestras)

        senal_2d[canal_idx, :] = canal_original + ruido
        self.senal_trabajo = senal_2d
        return canal_original, senal_2d[canal_idx, :]

    def restaurar_senal_original(self):
        if self.datos_originales is not None:
            self.senal_trabajo = self.datos_originales.copy()

    def obtener_comparacion_canal(self, canal_idx):
        senal_2d = self.obtener_senal_2d()
        if senal_2d is None:
            return None, None

        if self.datos_originales.ndim == 2:
            original = self.datos_originales[canal_idx, :]
        else:
            original = self.datos_originales[canal_idx, :].reshape(-1)

        modificada = senal_2d[canal_idx, :]
        return original, modificada

    def calcular_promedio_std_por_eje(self, eje=0):
        senal_2d = self.obtener_senal_2d()
        if senal_2d is None:
            return None, None
        promedio = np.mean(senal_2d, axis=eje)
        desviacion = np.std(senal_2d, axis=eje)
        return promedio, desviacion

    def obtener_info_eje(self, eje):
        if eje == 0:
            return "Eje 0 - por canal"
        else:
            return "Eje 1 - por muestra"

    def obtener_resumen_datos(self):
        if self.datos_originales is None:
            return None
        return {
            'forma': self.forma_datos,
            'dimensiones': self.datos_originales.ndim,
            'canales': self.num_canales,
            'tipo_datos': str(self.datos_originales.dtype),
            'minimo': float(np.min(self.datos_originales)),
            'maximo': float(np.max(self.datos_originales)),
            'promedio': float(np.mean(self.datos_originales))
        }