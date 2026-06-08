import pandas as pd


class ModeloTabular:
    def __init__(self):
        self.df = None
        self.ruta_archivo = None

    def cargar_archivo(self, ruta_archivo):
        self.ruta_archivo = ruta_archivo

        if ruta_archivo.lower().endswith(".csv"):
            self.df = pd.read_csv(ruta_archivo, sep=None, engine="python")
        elif ruta_archivo.lower().endswith(".xlsx"):
            self.df = pd.read_excel(ruta_archivo)
        else:
            raise ValueError("Formato no soportado")

        return self.df

    def obtener_columnas(self):
        if self.df is None:
            return []
        return list(self.df.columns)

    def obtener_info_dataframe(self):
        if self.df is None:
            return pd.DataFrame()

        filas = []
        for col in self.df.columns:
            filas.append({
                "columna": col,
                "no_nulos": self.df[col].notnull().sum(),
                "tipo_dato": str(self.df[col].dtype)
            })

        return pd.DataFrame(filas)

    def obtener_describe(self):
        if self.df is None:
            return pd.DataFrame()

        return self.df.describe(include="all").fillna("")

    def obtener_datos_columnas(self, columnas):
        if self.df is None:
            return pd.DataFrame()

        return self.df[columnas]

    def obtener_datos_scatter(self, columna_x, columna_y):
        if self.df is None:
            return None, None

        return self.df[columna_x], self.df[columna_y]