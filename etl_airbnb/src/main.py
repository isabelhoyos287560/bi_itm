"""
main.py
-------
Script principal del proceso ETL Airbnb Buenos Aires.

Orquesta las tres fases del proceso en orden:
  1. Extraccion: conecta a MongoDB y carga los datos en DataFrames.
  2. Transformacion: limpia, estandariza y enriquece los datos.
  3. Carga: inserta en SQLite y exporta a XLSX.

Uso:
    python src/main.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extraccion import Extraccion
from transformacion import Transformacion
from carga import Carga
from logger import Logger
from config import RUTA_LOGS


def main():
    log = Logger("main", ruta_logs=RUTA_LOGS)
    log.info("=" * 60)
    log.info("INICIO DEL PROCESO ETL - AIRBNB BUENOS AIRES")
    log.info("=" * 60)

    # ── FASE 1: Extraccion ─────────────────────────────────────────────────────
    log.info("FASE 1: Extraccion")
    ext = Extraccion()
    df_listings, df_reviews, df_calendar = ext.extraer_todo()
    ext.cerrar_conexion()

    # ── FASE 2: Transformacion ─────────────────────────────────────────────────
    log.info("FASE 2: Transformacion")
    trans = Transformacion(df_listings, df_reviews, df_calendar)
    df_l_ok, df_r_ok, df_c_ok = trans.transformar_todo()

    # ── FASE 3: Carga ──────────────────────────────────────────────────────────
    log.info("FASE 3: Carga")
    carga = Carga(df_l_ok, df_r_ok, df_c_ok)
    carga.cargar_todo()

    log.info("=" * 60)
    log.info("PROCESO ETL FINALIZADO CORRECTAMENTE")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
