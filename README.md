# BioCoreNexus

Aplicativo de escritorio para carga, procesamiento y análisis de datos biomédicos desarrollado en Python con arquitectura Modelo-Vista-Controlador (MVC). Permite trabajar con imagenes medicas DICOM y NIfTI, senales biomedicas en formato MAT y datos tabulares en CSV o Excel.

Proyecto final - Informatica II 2026-1  
Universidad de Antioquia - Bioingenieria

---

## Requisitos del sistema

- Python 3.10 o superior  
- Anaconda (recomendado)  
- MongoDB Atlas (conexion incluida en el codigo)  
- Camara web funcional para la captura de sesion  
---

## Instalacion de dependencias

Desde Anaconda Prompt o terminal, dentro de la carpeta del proyecto:

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install pyqt5 pymongo opencv-python numpy pandas scipy pydicom nibabel matplotlib scikit-image
```

---

## Estructura del proyecto

```
ProyectoFinalInfo2/
├── main.py
├── requirements.txt
├── controlador/
│   ├── controlador_principal.py
│   ├── controlador_autenticacion.py
│   ├── controlador_camara.py
│   ├── controlador_imagenes.py
│   ├── controlador_senales.py
│   └── controlador_tablas.py
├── modelo/
│   ├── modelo_autenticacion.py
│   ├── modelo_camara.py
│   ├── modelo_dicom.py
│   ├── modelo_nifti.py
│   ├── modelo_senales.py
│   └── modelo_tabular.py
├── vista/
│   ├── vista_login.py
│   ├── vista_principal.py
│   ├── vista_imagen.py
│   ├── vista_senales.py
│   ├── vista_tablas.py
│   └── ui/
│       ├── login.ui
│       ├── ventana_principal.ui
│       ├── modulo_imagenes.ui
│       ├── modulo_senales.ui
│       └── modulo_tablas.ui
├── datos/
│   ├── Diabetes.csv
│   └── pacientes.csv
└── recursos/
    └── recursos_rc.py
```

---

## Como ejecutar

Desde la carpeta raiz del proyecto:

```bash
python main.py
```

---

## Base de datos

El proyecto usa MongoDB Atlas. La conexion esta configurada en `modelo/modelo_autenticacion.py` y `modelo/modelo_camara.py`.

Usuarios de prueba registrados en la base de datos:

| Nombre | Contrasena | Rol |
|---|---|---|
| Dr. Alejandro Mendoza | udea2026 | administrador |
| Dra. Natalia Arevalo | biocore99 | usuario |

---

## Arquitectura

El proyecto sigue el patron MVC:

- **Modelo**: logica de negocio, procesamiento de datos y conexion a la base de datos  
- **Vista**: interfaces graficas disenadas en Qt Designer y cargadas con `uic.loadUi`  
- **Controlador**: manejo de eventos, comunicacion entre modelo y vista  

---

## Archivos de prueba recomendados

- Imagenes DICOM: archivos `.dcm` descargables desde [The Cancer Imaging Archive](https://www.cancerimagingarchive.net)  
- Senales MAT: archivos `.mat` descargables desde [PhysioNet](https://physionet.org)  
- Datos tabulares: archivos `.csv` o `.xlsx` con datos medicos, disponibles en [Kaggle](https://www.kaggle.com)
