import os
import cv2
import time
from pymongo import MongoClient
from datetime import datetime


class ModeloCamara:
    def __init__(self):
        self.carpeta_fotos = "datos/fotos"
        os.makedirs("datos", exist_ok=True)
        os.makedirs(self.carpeta_fotos, exist_ok=True)

        cliente = MongoClient("mongodb+srv://biocore_user:bio2026@biocorenexus.hvmx8zp.mongodb.net/?appName=BioCoreNexus")
        self.db = cliente["biocore_nexus"]
        self.coleccion_sesiones = self.db["sesiones"]

    def capturar_foto(self, id_usuario):
        camara = cv2.VideoCapture(0)
        if not camara.isOpened():
            raise Exception("No se pudo abrir la cámara.")

        fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        inicio = time.time()

        while True:
            ret, frame = camara.read()
            if not ret:
                camara.release()
                cv2.destroyAllWindows()
                raise Exception("No se pudo leer el frame.")

            segundos_restantes = 3 - int(time.time() - inicio)
            cv2.putText(frame, f"Capturando en {segundos_restantes}s...",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.imshow("Captura de Usuario", frame)
            cv2.waitKey(1)

            if time.time() - inicio >= 3:
                nombre_archivo = f"usuario_{id_usuario}_{fecha_actual}.jpg"
                ruta_guardado = os.path.join(self.carpeta_fotos, nombre_archivo)
                cv2.imwrite(ruta_guardado, frame)
                break

        camara.release()
        cv2.destroyAllWindows()
        self.guardar_registro_foto(id_usuario, ruta_guardado)
        return ruta_guardado

    def guardar_registro_foto(self, id_usuario, ruta_foto):
        registro = {
            "id_usuario": id_usuario,
            "ruta_foto": ruta_foto,
            "fecha_captura": datetime.now()
        }
        self.coleccion_sesiones.insert_one(registro)
        print(f"[+] Sesión guardada en Base de Datos para usuario {id_usuario}")