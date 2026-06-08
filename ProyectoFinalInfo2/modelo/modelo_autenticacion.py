from pymongo import MongoClient
class ModeloAutenticacion:
    def __init__(self):
        self.cliente = MongoClient("mongodb://localhost:27017/")
        self.db = self.cliente["biocore_nexus"]
        self.coleccion_usuarios = self.db["users"]
        self._insertar_usuarios_semilla()

    def _insertar_usuarios_semilla(self):
        if self.coleccion_usuarios.count_documents({}) == 0:
            usuarios = [
                {"id": "1001", "nombre": "Dr. Alejandro Mendoza", "password": "udea2026",  "rol": "administrador"},
                {"id": "1002", "nombre": "Dra. Natalia Arevalo",  "password": "biocore99", "rol": "usuario"},
            ]
            self.coleccion_usuarios.insert_many(usuarios)
            print("[+] Usuarios semilla creados en MongoDB.")

    def validar_usuario(self, nombre, password):
        try:
            usuario = self.coleccion_usuarios.find_one(
                {"nombre": nombre, "password": password}
            )
            if usuario:
                return {
                    "id":     usuario["id"],
                    "nombre": usuario["nombre"],
                    "rol":    usuario["rol"]
                }
            return None
        except Exception as e:
            print(f"[-] Error al validar usuario: {e}")
            return None