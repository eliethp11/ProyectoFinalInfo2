from PyQt5.QtWidgets import QMessageBox
from modelo.modelo_camara import ModeloCamara


class ControladorCamara:
    def __init__(self):
        self.modelo = ModeloCamara()

    def capturar_foto_usuario(self, usuario_actual, ventana_padre=None):
        if not usuario_actual:
            QMessageBox.warning(
                ventana_padre,
                "Aviso",
                "No hay un usuario autenticado."
            )
            return

        try:
            if isinstance(usuario_actual, dict):
                id_usuario = usuario_actual.get("id", 1)
            else:
                id_usuario = 1

            ruta_foto = self.modelo.capturar_foto(id_usuario)

            if ruta_foto:
                QMessageBox.information(
                    ventana_padre,
                    "Foto guardada",
                    f"Foto capturada correctamente.\nRuta: {ruta_foto}"
                )
            else:
                QMessageBox.information(
                    ventana_padre,
                    "Cancelado",
                    "No se capturó ninguna foto."
                )

        except Exception as e:
            QMessageBox.critical(
                ventana_padre,
                "Error",
                str(e)
            )