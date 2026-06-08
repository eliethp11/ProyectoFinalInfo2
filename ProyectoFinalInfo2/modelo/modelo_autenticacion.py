class ModeloAutenticacion:
    def __init__(self):
        self.usuarios = [
            {
                "id": 1,
                "nombre": "admin",
                "password": "1234",
                "rol": "administrador"
            },
            {
                "id": 2,
                "nombre": "usuario",
                "password": "1234",
                "rol": "usuario"
            }
        ]

    def validar_usuario(self, nombre, password):
        for usuario in self.usuarios:
            if usuario["nombre"] == nombre and usuario["password"] == password:
                return usuario
        return None