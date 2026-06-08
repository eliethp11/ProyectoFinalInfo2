import os
import cv2
import sqlite3
from datetime import datetime


class ModeloCamara:
    def __init__(self):
        self.base_datos = "datos/proyecto.db"
        self.carpeta_fotos = "datos/fotos"

        os.makedirs("datos", exist_ok=True)
        os.makedirs(self.carpeta_fotos, exist_ok=True)

        self.inicializar_bd()

    def inicializar_bd(self):
        conexion = sqlite3.connect(self.base_datos)
        cursor = conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sesiones_fotos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                ruta_foto TEXT NOT NULL,
                fecha_sesion TEXT NOT NULL
            )
        """)

        conexion.commit()
        conexion.close()

    def capturar_foto(self, id_usuario):
        camara = cv2.VideoCapture(0)

        if not camara.isOpened():
            raise Exception("No se pudo abrir la cámara.")

        ruta_guardado = None
        fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        while True:
            ret, frame = camara.read()

            if not ret:
                camara.release()
                cv2.destroyAllWindows()
                raise Exception("No se pudo leer el frame de la cámara.")

            cv2.putText(
                frame,
                "Presiona C para capturar / ESC para salir",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.imshow("Captura de Usuario", frame)

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == ord('c'):
                nombre_archivo = f"usuario_{id_usuario}_{fecha_actual}.jpg"
                ruta_guardado = os.path.join(self.carpeta_fotos, nombre_archivo)
                cv2.imwrite(ruta_guardado, frame)
                break

            elif tecla == 27:
                break

        camara.release()
        cv2.destroyAllWindows()

        if ruta_guardado:
            self.guardar_registro_foto(id_usuario, ruta_guardado)
            return ruta_guardado

        return None

    def guardar_registro_foto(self, id_usuario, ruta_foto):
        conexion = sqlite3.connect(self.base_datos)
        cursor = conexion.cursor()

        fecha_sesion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO sesiones_fotos (id_usuario, ruta_foto, fecha_sesion)
            VALUES (?, ?, ?)
        """, (id_usuario, ruta_foto, fecha_sesion))

        conexion.commit()
        conexion.close()