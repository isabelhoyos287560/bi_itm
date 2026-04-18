"""
logger.py
---------
Modulo centralizado de manejo de logs para el proceso ETL de Airbnb Mexico.

Provee una clase Logger reutilizable que genera un archivo de log por ejecucion
con el formato: logs/log_YYYYMMDD_HHMM.txt

Uso:
    from logger import Logger
    log = Logger("extraccion")
    log.info("Conexion exitosa a MongoDB")
    log.warning("Campo nulo detectado en columna price")
    log.error("No se pudo conectar a la base de datos")
"""

import logging
import os
from datetime import datetime


class Logger:
    """
    Clase reutilizable para manejo de logs del proceso ETL.

    Genera un archivo de log por ejecucion con niveles INFO, WARNING y ERROR.
    Tambien muestra los mensajes en consola de forma simultanea.

    Attributes:
        nombre (str): Nombre del modulo que instancia el logger (extraccion, transformacion, carga).
        ruta_logs (str): Ruta donde se almacenan los archivos de log.
        logger (logging.Logger): Instancia interna del logger de Python.
    """

    def __init__(self, nombre: str, ruta_logs: str = "logs"):
        """
        Inicializa el logger y crea el archivo de log para esta ejecucion.

        Args:
            nombre (str): Nombre del modulo o componente que usa el logger.
            ruta_logs (str): Carpeta donde se guardan los logs. Por defecto 'logs'.
        """
        self.nombre = nombre
        self.ruta_logs = ruta_logs

        # Crear carpeta de logs si no existe
        os.makedirs(self.ruta_logs, exist_ok=True)

        # Nombre del archivo: log_YYYYMMDD_HHMM.txt
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nombre_archivo = f"log_{nombre}_{timestamp}.txt"
        ruta_archivo = os.path.join(self.ruta_logs, nombre_archivo)

        # Configurar el logger interno de Python
        self.logger = logging.getLogger(f"{nombre}_{timestamp}")
        self.logger.setLevel(logging.DEBUG)

        # Evitar handlers duplicados si se instancia varias veces
        if not self.logger.handlers:
            # Handler para archivo
            handler_archivo = logging.FileHandler(ruta_archivo, encoding="utf-8")
            handler_archivo.setLevel(logging.DEBUG)

            # Handler para consola
            handler_consola = logging.StreamHandler()
            handler_consola.setLevel(logging.DEBUG)

            # Formato: fecha hora - nivel - mensaje
            formato = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler_archivo.setFormatter(formato)
            handler_consola.setFormatter(formato)

            self.logger.addHandler(handler_archivo)
            self.logger.addHandler(handler_consola)

        self.info(f"Logger iniciado para el modulo: {nombre}")
        self.info(f"Archivo de log: {ruta_archivo}")

    def info(self, mensaje: str) -> None:
        """Registra un mensaje de nivel INFO."""
        self.logger.info(mensaje)

    def warning(self, mensaje: str) -> None:
        """Registra un mensaje de nivel WARNING."""
        self.logger.warning(mensaje)

    def error(self, mensaje: str) -> None:
        """Registra un mensaje de nivel ERROR."""
        self.logger.error(mensaje)
