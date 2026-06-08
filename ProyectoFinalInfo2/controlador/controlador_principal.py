from controlador.controlador_camara import ControladorCamara
from controlador.controlador_tablas import ControladorTablas
from PyQt5.QtWidgets import QMessageBox
from vista.vista_login import VistaLogin
from controlador.controlador_autenticacion import ControladorAutenticacion


class ControladorPrincipal:
    def __init__(self, vista_principal):
        self.vista_principal = vista_principal
        self.vista_login = VistaLogin()
        self.usuario_actual = None
        self.controlador_tablas = ControladorTablas()

        self.controlador_autenticacion = ControladorAutenticacion(
            self.vista_login,
            self
        )

        self.configurar_eventos_principales()
        self.mostrar_login_inicial()
        self.controlador_camara = ControladorCamara()

    def configurar_eventos_principales(self):
        if hasattr(self.vista_principal, "btn_salir"):
            self.vista_principal.btn_salir.clicked.connect(self.cerrar_aplicacion)

        if hasattr(self.vista_principal, "btn_modulo_imagenes"):
            self.vista_principal.btn_modulo_imagenes.clicked.connect(
                self.abrir_modulo_imagenes
            )

        if hasattr(self.vista_principal, "btn_modulo_senales"):
            self.vista_principal.btn_modulo_senales.clicked.connect(
                self.abrir_modulo_senales
            )

        if hasattr(self.vista_principal, "btn_modulo_tablas"):
            self.vista_principal.btn_modulo_tablas.clicked.connect(
                self.abrir_modulo_tablas
            )
        if hasattr(self.vista_principal, "btn_capturar_foto"):
            self.vista_principal.btn_capturar_foto.clicked.connect(
                self.abrir_captura_foto
             )

    def mostrar_login_inicial(self):
        self.vista_login.show()

    def login_exitoso(self, usuario):
        self.usuario_actual = usuario
        self.vista_login.close()
        self.abrir_captura_foto()
        self.vista_principal.show()

    def abrir_captura_foto(self):
        self.controlador_camara.capturar_foto_usuario(self.usuario_actual, self.vista_principal)
        
    def abrir_modulo_imagenes(self):
        QMessageBox.information(
            self.vista_principal,
            "Módulo de Imágenes",
            "Aquí irá el módulo de procesamiento de imágenes médicas."
        )

    def abrir_modulo_senales(self):
        QMessageBox.information(
            self.vista_principal,
            "Módulo de Señales",
            "Aquí irá el módulo de procesamiento de señales biomédicas."
        )

    def abrir_modulo_tablas(self):
        self.controlador_tablas.mostrar()

    def cerrar_aplicacion(self):
        self.vista_principal.close()