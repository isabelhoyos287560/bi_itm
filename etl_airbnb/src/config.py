"""
config.py
---------
Configuracion central del proyecto ETL Airbnb Buenos Aires.

Lee las variables de entorno desde el archivo .env usando python-dotenv.
Centraliza todos los parametros de conexion y rutas del proyecto.
"""

import os
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

# ── MongoDB ────────────────────────────────────────────────────────────────────
MONGODB_URI         = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DATABASE    = os.getenv("MONGODB_DATABASE", "airbnb_itm")
MONGODB_TIMEOUT_MS  = int(os.getenv("MONGODB_TIMEOUT_MS", "5000"))

# Nombres de las colecciones en MongoDB
COLECCION_LISTINGS  = "Listings"
COLECCION_REVIEWS   = "Reviews"
COLECCION_CALENDAR  = "Calendar"

# ── Rutas del proyecto ─────────────────────────────────────────────────────────
RUTA_DATA           = os.path.join("src", "data")
RUTA_PROCESSED      = os.path.join("src", "data", "processed")
RUTA_LOGS           = "logs"

# ── SQLite ─────────────────────────────────────────────────────────────────────
SQLITE_DB           = os.path.join(RUTA_DATA, "etl_airbnb.db")
