"""
extraccion.py
-------------
Modulo de extraccion de datos del proceso ETL Airbnb Buenos Aires.

Contiene la clase Extraccion, responsable de:
  - establecer conexion con la base de datos MongoDB local,
  - consultar cada coleccion (Listings, Reviews, Calendar),
  - cargar los datos en DataFrames de pandas,
  - registrar en log la conexion realizada y la cantidad de registros extraidos.

Uso:
    from extraccion import Extraccion
    ext = Extraccion()
    df_listings, df_reviews, df_calendar = ext.extraer_todo()
"""

import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    MONGODB_URI,
    MONGODB_DATABASE,
    MONGODB_TIMEOUT_MS,
    COLECCION_LISTINGS,
    COLECCION_REVIEWS,
    COLECCION_CALENDAR,
    RUTA_LOGS,
)
from logger import Logger


class Extraccion:
    """
    Clase encargada de extraer datos desde MongoDB hacia DataFrames de pandas.

    Establece la conexion con la base de datos local de MongoDB y expone
    metodos para extraer cada coleccion de forma individual o todas juntas.

    Attributes:
        log (Logger): Instancia del logger para registrar eventos.
        cliente (MongoClient): Cliente de conexion a MongoDB.
        db: Base de datos activa en MongoDB.
    """

    def __init__(self):
        """
        Inicializa el logger y establece la conexion con MongoDB.
        Registra en log si la conexion fue exitosa o si hubo un error.
        """
        self.log = Logger("extraccion", ruta_logs=RUTA_LOGS)
        self.cliente = None
        self.db = None
        self._conectar()

    def _conectar(self) -> None:
        """
        Establece la conexion a la base de datos MongoDB.

        Registra en log la URI de conexion y el nombre de la base de datos.
        En caso de fallo registra el error y lanza la excepcion.

        Raises:
            ConnectionFailure: Si MongoDB no esta disponible.
            ServerSelectionTimeoutError: Si el servidor no responde en el tiempo configurado.
        """
        try:
            self.log.info(f"Intentando conectar a MongoDB: {MONGODB_URI}")
            self.cliente = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=MONGODB_TIMEOUT_MS
            )
            # Forzar la conexion real con un ping
            self.cliente.admin.command("ping")
            self.db = self.cliente[MONGODB_DATABASE]
            self.log.info(f"Conexion exitosa a la base de datos: '{MONGODB_DATABASE}'")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.log.error(f"Error al conectar a MongoDB: {e}")
            raise

    def extraer_coleccion(self, nombre_coleccion: str) -> pd.DataFrame:
        """
        Extrae todos los documentos de una coleccion de MongoDB y los retorna
        como un DataFrame de pandas.

        Args:
            nombre_coleccion (str): Nombre de la coleccion a consultar.

        Returns:
            pd.DataFrame: DataFrame con todos los registros de la coleccion.
                          Retorna un DataFrame vacio si ocurre un error.
        """
        try:
            self.log.info(f"Extrayendo coleccion: '{nombre_coleccion}'")
            coleccion = self.db[nombre_coleccion]
            cursor = coleccion.find({}, {"_id": 0})  # excluir el _id de MongoDB
            df = pd.DataFrame(list(cursor))

            if df.empty:
                self.log.warning(f"La coleccion '{nombre_coleccion}' esta vacia o no existe.")
            else:
                self.log.info(
                    f"Coleccion '{nombre_coleccion}' extraida correctamente. "
                    f"Registros: {len(df):,} | Columnas: {df.shape[1]}"
                )
            return df

        except Exception as e:
            self.log.error(f"Error al extraer la coleccion '{nombre_coleccion}': {e}")
            return pd.DataFrame()

    def extraer_listings(self) -> pd.DataFrame:
        """
        Extrae la coleccion Listings de MongoDB.

        Returns:
            pd.DataFrame: DataFrame con los datos de listings (alojamientos).
        """
        return self.extraer_coleccion(COLECCION_LISTINGS)

    def extraer_reviews(self) -> pd.DataFrame:
        """
        Extrae la coleccion Reviews de MongoDB.

        Returns:
            pd.DataFrame: DataFrame con los datos de resenas de los alojamientos.
        """
        return self.extraer_coleccion(COLECCION_REVIEWS)

    def extraer_calendar(self) -> pd.DataFrame:
        """
        Extrae la coleccion Calendar de MongoDB.

        Returns:
            pd.DataFrame: DataFrame con los datos de disponibilidad y precios por fecha.
        """
        return self.extraer_coleccion(COLECCION_CALENDAR)

    def extraer_todo(self) -> tuple:
        """
        Extrae las tres colecciones principales del proyecto en un solo llamado.

        Returns:
            tuple: (df_listings, df_reviews, df_calendar) como DataFrames de pandas.
        """
        self.log.info("Iniciando extraccion completa de todas las colecciones.")
        df_listings  = self.extraer_listings()
        df_reviews   = self.extraer_reviews()
        df_calendar  = self.extraer_calendar()

        self.log.info(
            f"Extraccion finalizada. Resumen: "
            f"Listings={len(df_listings):,} | "
            f"Reviews={len(df_reviews):,} | "
            f"Calendar={len(df_calendar):,}"
        )
        return df_listings, df_reviews, df_calendar

    def cerrar_conexion(self) -> None:
        """Cierra la conexion con MongoDB y registra el evento en el log."""
        if self.cliente:
            self.cliente.close()
            self.log.info("Conexion a MongoDB cerrada correctamente.")


# ── Ejecucion directa para prueba rapida ──────────────────────────────────────
if __name__ == "__main__":
    ext = Extraccion()
    df_listings, df_reviews, df_calendar = ext.extraer_todo()
    print("\n--- Vista previa de Listings ---")
    print(df_listings.head(3))
    print("\n--- Vista previa de Reviews ---")
    print(df_reviews.head(3))
    print("\n--- Vista previa de Calendar ---")
    print(df_calendar.head(3))
    ext.cerrar_conexion()
