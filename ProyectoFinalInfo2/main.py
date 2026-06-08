import sys
import os
from PyQt5.QtWidgets import QApplication

# Si aún no has creado recursos_rc.py, deja esta línea comentada.
# import recursos.recursos_rc

directorio_actual = os.path.dirname(os.path.abspath(__file__))
sys.path.append(directorio_actual)

from vista.vista_principal import VistaPrincipal
from controlador.controlador_principal import ControladorPrincipal


def main():
    app = QApplication(sys.argv)

    vista_principal = VistaPrincipal()
    controlador_principal = ControladorPrincipal(vista_principal)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()