"""
carga.py
--------
Modulo de carga de datos del proceso ETL Airbnb Mexico.

Contiene la clase Carga, responsable de:
  - insertar los DataFrames transformados en una base de datos SQLite,
  - exportar los datos a archivos XLSX,
  - verificar que los registros se hayan cargado correctamente,
  - registrar en logs los eventos principales del proceso.

Uso:
    from carga import Carga
    carga = Carga(df_listings, df_reviews, df_calendar)
    carga.cargar_todo()
"""

import os
import sqlite3
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SQLITE_DB, RUTA_PROCESSED, RUTA_LOGS
from logger import Logger


class Carga:
    """
    Clase encargada de cargar los DataFrames transformados en SQLite y en XLSX.

    Implementa una estrategia de carga doble:
      - Tablas en SQLite para consultas analiticas y validacion.
      - Archivos XLSX para consumo directo por parte del usuario.

    Attributes:
        log (Logger): Instancia del logger para registrar eventos.
        df_listings (pd.DataFrame): DataFrame limpio de listings.
        df_reviews (pd.DataFrame): DataFrame limpio de reviews.
        df_calendar (pd.DataFrame): DataFrame limpio de calendar.
        ruta_db (str): Ruta del archivo SQLite.
        ruta_processed (str): Carpeta de salidas procesadas.
    """

    def __init__(
        self,
        df_listings: pd.DataFrame,
        df_reviews: pd.DataFrame,
        df_calendar: pd.DataFrame
    ):
        """
        Inicializa la clase Carga con los DataFrames transformados.

        Args:
            df_listings (pd.DataFrame): Listings ya transformados.
            df_reviews (pd.DataFrame): Reviews ya transformados.
            df_calendar (pd.DataFrame): Calendar ya transformados.
        """
        self.log = Logger("carga", ruta_logs=RUTA_LOGS)
        self.df_listings  = df_listings
        self.df_reviews   = df_reviews
        self.df_calendar  = df_calendar
        self.ruta_db      = SQLITE_DB
        self.ruta_processed = RUTA_PROCESSED

        # Crear carpeta de salidas si no existe
        os.makedirs(self.ruta_processed, exist_ok=True)
        self.log.info("Clase Carga inicializada.")

    # ── Carga en SQLite ────────────────────────────────────────────────────────

    def cargar_sqlite(self) -> None:
        """
        Inserta los tres DataFrames transformados en una base de datos SQLite local.

        Usa la estrategia 'replace' para reemplazar la tabla si ya existe,
        lo que permite ejecutar el ETL multiples veces sin errores de duplicados.

        Tablas generadas en SQLite:
          - listings
          - reviews
          - calendar

        Registra en log la cantidad de registros cargados en cada tabla.
        """
        self.log.info(f"Iniciando carga en SQLite: {self.ruta_db}")
        try:
            conexion = sqlite3.connect(self.ruta_db)

            # Cargar listings
            self.df_listings.to_sql("listings", conexion, if_exists="replace", index=False)
            self.log.info(f"Tabla 'listings' cargada en SQLite. Registros: {len(self.df_listings):,}")

            # Cargar reviews
            self.df_reviews.to_sql("reviews", conexion, if_exists="replace", index=False)
            self.log.info(f"Tabla 'reviews' cargada en SQLite. Registros: {len(self.df_reviews):,}")

            # Cargar calendar
            self.df_calendar.to_sql("calendar", conexion, if_exists="replace", index=False)
            self.log.info(f"Tabla 'calendar' cargada en SQLite. Registros: {len(self.df_calendar):,}")

            conexion.close()
            self.log.info("Carga en SQLite finalizada y conexion cerrada.")

        except Exception as e:
            self.log.error(f"Error durante la carga en SQLite: {e}")
            raise

    # ── Verificacion de carga ──────────────────────────────────────────────────

    def verificar_carga(self) -> None:
        """
        Verifica que las tablas existan en SQLite y que el conteo de registros
        coincida con los DataFrames cargados.

        Registra en log el resultado de la verificacion para cada tabla.
        """
        self.log.info("Verificando integridad de la carga en SQLite.")
        try:
            conexion = sqlite3.connect(self.ruta_db)
            tablas = {
                "listings":  len(self.df_listings),
                "reviews":   len(self.df_reviews),
                "calendar":  len(self.df_calendar),
            }

            for tabla, esperado in tablas.items():
                resultado = pd.read_sql(f"SELECT COUNT(*) AS total FROM {tabla}", conexion)
                cargado = resultado["total"].iloc[0]

                if cargado == esperado:
                    self.log.info(
                        f"[OK] Tabla '{tabla}': {cargado:,} registros verificados correctamente."
                    )
                else:
                    self.log.warning(
                        f"[ALERTA] Tabla '{tabla}': esperados {esperado:,}, encontrados {cargado:,}."
                    )

            conexion.close()

        except Exception as e:
            self.log.error(f"Error durante la verificacion de carga: {e}")
            raise

    # ── Exportacion a XLSX ─────────────────────────────────────────────────────

    def exportar_xlsx(self) -> None:
        """
        Exporta los tres DataFrames transformados a archivos XLSX individuales
        dentro de la carpeta de salidas procesadas.

        Archivos generados:
          - src/data/processed/listings_transformado.xlsx
          - src/data/processed/reviews_transformado.xlsx
          - src/data/processed/calendar_transformado.xlsx

        Registra en log la ruta y el numero de registros de cada archivo exportado.
        """
        self.log.info("Iniciando exportacion a archivos XLSX.")
        exportaciones = {
            "listings_transformado.xlsx":  self.df_listings,
            "reviews_transformado.xlsx":   self.df_reviews,
            "calendar_transformado.xlsx":  self.df_calendar,
        }

        for nombre_archivo, df in exportaciones.items():
            ruta_xlsx = os.path.join(self.ruta_processed, nombre_archivo)
            try:
                df.to_excel(ruta_xlsx, index=False, engine="openpyxl")
                self.log.info(
                    f"Archivo exportado: '{ruta_xlsx}' | Registros: {len(df):,}"
                )
            except Exception as e:
                self.log.error(f"Error al exportar '{nombre_archivo}': {e}")

        self.log.info("Exportacion a XLSX finalizada.")

    # ── Pipeline completo de carga ─────────────────────────────────────────────

    def cargar_todo(self) -> None:
        """
        Ejecuta el pipeline completo de carga:
          1. Carga los tres DataFrames en SQLite.
          2. Verifica la integridad de la carga.
          3. Exporta los DataFrames a archivos XLSX.
        """
        self.log.info("Iniciando pipeline completo de carga.")
        self.cargar_sqlite()
        self.verificar_carga()
        self.exportar_xlsx()
        self.log.info("Pipeline de carga finalizado correctamente.")


# ── Ejecucion directa ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    from extraccion import Extraccion
    from transformacion import Transformacion

    # Extraccion
    ext = Extraccion()
    df_l, df_r, df_c = ext.extraer_todo()
    ext.cerrar_conexion()

    # Transformacion
    trans = Transformacion(df_l, df_r, df_c)
    df_l_ok, df_r_ok, df_c_ok = trans.transformar_todo()

    # Carga
    carga = Carga(df_l_ok, df_r_ok, df_c_ok)
    carga.cargar_todo()
