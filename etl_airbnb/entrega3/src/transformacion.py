"""
transformacion.py
-----------------
Modulo de transformacion de datos del proceso ETL Airbnb Mexico.

Contiene la clase Transformacion, responsable de:
  - limpiar valores nulos y duplicados,
  - normalizar precios (eliminar $ y comas, convertir a float),
  - convertir fechas al formato estandar YYYY-MM-DD,
  - derivar variables de tiempo (anio, mes, dia, trimestre),
  - categorizar precios por rangos,
  - expandir campos anidados como 'amenities',
  - generar DataFrames limpios y listos para la carga.

Uso:
    from transformacion import Transformacion
    trans = Transformacion(df_listings, df_reviews, df_calendar)
    listings_limpio, reviews_limpio, calendar_limpio = trans.transformar_todo()
"""

import pandas as pd
import numpy as np
import ast
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import RUTA_LOGS
from logger import Logger


class Transformacion:
    """
    Clase que implementa todas las transformaciones del proceso ETL para los
    datasets de Airbnb de Mexico.

    Recibe los DataFrames crudos extraidos de MongoDB y aplica limpieza,
    estandarizacion y enriquecimiento de datos.

    Attributes:
        log (Logger): Instancia del logger para registrar eventos.
        df_listings (pd.DataFrame): DataFrame crudo de listings.
        df_reviews (pd.DataFrame): DataFrame crudo de reviews.
        df_calendar (pd.DataFrame): DataFrame crudo de calendar.
    """

    def __init__(
        self,
        df_listings: pd.DataFrame,
        df_reviews: pd.DataFrame,
        df_calendar: pd.DataFrame
    ):
        """
        Inicializa la clase con los DataFrames crudos y el logger.

        Args:
            df_listings (pd.DataFrame): Datos de alojamientos desde MongoDB.
            df_reviews (pd.DataFrame): Datos de resenas desde MongoDB.
            df_calendar (pd.DataFrame): Datos de calendario desde MongoDB.
        """
        self.log = Logger("transformacion", ruta_logs=RUTA_LOGS)
        # Trabajamos sobre copias para no modificar los DataFrames originales
        self.df_listings  = df_listings.copy()
        self.df_reviews   = df_reviews.copy()
        self.df_calendar  = df_calendar.copy()
        self.log.info("Clase Transformacion inicializada con los tres DataFrames.")

    # ── Utilidades generales ───────────────────────────────────────────────────

    def _limpiar_nulos_y_duplicados(self, df: pd.DataFrame, nombre: str) -> pd.DataFrame:
        """
        Elimina duplicados exactos y registra el impacto en el log.
        Los nulos se conservan por defecto; columnas criticas se tratan por separado.

        Args:
            df (pd.DataFrame): DataFrame a limpiar.
            nombre (str): Nombre del DataFrame para el log.

        Returns:
            pd.DataFrame: DataFrame sin duplicados exactos.
        """
        registros_antes = len(df)
        cols_hashables = [
            col for col in df.columns 
            if not df[col].apply(lambda x: isinstance(x, (list, dict))).any()
        ]
        df = df.drop_duplicates(subset=cols_hashables)
        
        registros_despues = len(df)
        eliminados = registros_antes - registros_despues

        self.log.info(
            f"[{nombre}] Registros antes: {registros_antes:,} | "
            f"Despues: {registros_despues:,} | "
            f"Duplicados eliminados: {eliminados:,}"
        )
        if eliminados > 0:
            self.log.warning(f"[{nombre}] Se eliminaron {eliminados:,} registros duplicados.")
        return df

    def _normalizar_precio(self, valor: any) -> float:
        """
        Convierte un campo de precio en formato texto ('$1,200.00') a float.
        Elimina el simbolo $, comas y espacios. Retorna NaN si no es convertible.

        Args:
            valor: Valor original del campo price (str, float o NaN).

        Returns:
            float: Precio numerico, o NaN si el valor es invalido.
        """
        try:
            if pd.isna(valor):
                return np.nan
            # Eliminar simbolos monetarios y comas
            limpio = str(valor).replace("$", "").replace(",", "").strip()
            return float(limpio)
        except (ValueError, TypeError):
            return np.nan

    def _convertir_fecha(self, df: pd.DataFrame, columna: str, nombre: str) -> pd.DataFrame:
        """
        Convierte una columna de fechas al formato estandar datetime (YYYY-MM-DD)
        y deriva columnas auxiliares: anio, mes, dia, trimestre.

        Args:
            df (pd.DataFrame): DataFrame con la columna de fecha.
            columna (str): Nombre de la columna de fecha a convertir.
            nombre (str): Nombre del DataFrame para el log.

        Returns:
            pd.DataFrame: DataFrame con la columna convertida y las derivadas agregadas.
        """
        if columna not in df.columns:
            self.log.warning(f"[{nombre}] La columna '{columna}' no existe. Se omite conversion.")
            return df

        df[columna] = pd.to_datetime(df[columna], errors="coerce")
        nulos_fecha = df[columna].isna().sum()
        if nulos_fecha > 0:
            self.log.warning(
                f"[{nombre}] {nulos_fecha:,} valores no convertibles en '{columna}' quedaron como NaT."
            )

        # Derivar variables de tiempo
        df[f"{columna}_anio"]      = df[columna].dt.year
        df[f"{columna}_mes"]       = df[columna].dt.month
        df[f"{columna}_dia"]       = df[columna].dt.day
        df[f"{columna}_trimestre"] = df[columna].dt.quarter

        # Estandarizar la columna original al formato YYYY-MM-DD como string
        df[columna] = df[columna].dt.strftime("%Y-%m-%d")

        self.log.info(
            f"[{nombre}] Columna '{columna}' convertida a fecha. "
            f"Variables derivadas: anio, mes, dia, trimestre."
        )
        return df

    def _categorizar_precio(self, precio: float) -> str:
        """
        Categoriza un precio numerico en rangos descriptivos.

        Rangos definidos basados en el analisis exploratorio de los datos
        de Airbnb Mexico:
          - Economico:   precio <= 50
          - Moderado:    50 < precio <= 150
          - Alto:        150 < precio <= 300
          - Premium:     precio > 300
          - Sin datos:   NaN

        Args:
            precio (float): Precio numerico del alojamiento.

        Returns:
            str: Categoria del precio.
        """
        if pd.isna(precio):
            return "Sin datos"
        elif precio <= 50:
            return "Economico"
        elif precio <= 150:
            return "Moderado"
        elif precio <= 300:
            return "Alto"
        else:
            return "Premium"

    # ── Transformacion de Listings ─────────────────────────────────────────────

    def transformar_listings(self) -> pd.DataFrame:
        """
        Aplica el pipeline completo de transformacion sobre el DataFrame de listings.

        Transformaciones aplicadas:
          1. Limpieza de duplicados.
          2. Normalizacion del campo 'price' a float.
          3. Normalizacion del campo 'weekly_price' y 'monthly_price' si existen.
          4. Conversion de 'last_scraped' y 'host_since' a fecha estandar.
          5. Categorizacion del precio por rangos.
          6. Expansion del campo 'amenities' (campo anidado tipo lista/string).
          7. Estandarizacion de texto en columnas clave.
          8. Relleno de nulos en columnas numericas criticas con 0.

        Returns:
            pd.DataFrame: DataFrame de listings transformado y listo para carga.
        """
        self.log.info("Iniciando transformacion de Listings.")
        df = self.df_listings.copy()

        # 1. Limpiar duplicados
        df = self._limpiar_nulos_y_duplicados(df, "Listings")

        # 2. Normalizar campo price
        if "price" in df.columns:
            df["price"] = df["price"].apply(self._normalizar_precio)
            nulos_price = df["price"].isna().sum()
            self.log.info(f"[Listings] 'price' convertido a float. Nulos resultantes: {nulos_price:,}")

        # 3. Normalizar precios adicionales si existen
        for campo_precio in ["weekly_price", "monthly_price", "security_deposit", "cleaning_fee"]:
            if campo_precio in df.columns:
                df[campo_precio] = df[campo_precio].apply(self._normalizar_precio)
                self.log.info(f"[Listings] Campo '{campo_precio}' normalizado a float.")

        # 4. Convertir columnas de fecha
        for col_fecha in ["last_scraped", "host_since", "calendar_last_scraped"]:
            df = self._convertir_fecha(df, col_fecha, "Listings")

        # 5. Categorizar precio
        if "price" in df.columns:
            df["price_categoria"] = df["price"].apply(self._categorizar_precio)
            self.log.info("[Listings] Columna 'price_categoria' creada con rangos: Economico, Moderado, Alto, Premium.")

        # 6. Expandir campo 'amenities' (viene como string representando una lista)
        # Se extrae la cantidad de amenities como variable numerica util
        if "amenities" in df.columns:
            def contar_amenities(valor):
                try:
                    if pd.isna(valor) or str(valor).strip() == "":
                        return 0
                    
                    texto = str(valor)
                    # Plan A: Intentar evaluarlo como estructura de Python (lista, tupla o set)
                    try:
                        estructura = ast.literal_eval(texto)
                        if isinstance(estructura, (list, tuple, set)):
                            return len(estructura)
                    except:
                        pass
                    
                    # Plan B: Si no es una estructura limpia, contamos las comas y sumamos 1
                    # Ej: "TV, Wifi, Cocina" tiene 2 comas -> son 3 elementos
                    return texto.count(',') + 1
                    
                except Exception:
                    return 0

            df["amenities_cantidad"] = df["amenities"].apply(contar_amenities)
            self.log.info("[Listings] Campo 'amenities_cantidad' derivado del campo 'amenities'.")

        # 7. Estandarizar texto en columnas de nombre y tipo
        for col_texto in ["name", "room_type", "property_type", "neighbourhood_cleansed"]:
            if col_texto in df.columns:
                df[col_texto] = df[col_texto].astype(str).str.strip().str.title()

        # 8. Rellenar nulos en columnas numericas criticas con 0
        for col_num in ["minimum_nights", "maximum_nights", "availability_365",
                         "number_of_reviews", "review_scores_rating"]:
            if col_num in df.columns:
                nulos_antes = df[col_num].isna().sum()
                df[col_num] = df[col_num].fillna(0)
                if nulos_antes > 0:
                    self.log.warning(
                        f"[Listings] {nulos_antes:,} nulos en '{col_num}' reemplazados por 0."
                    )

        self.log.info(f"[Listings] Transformacion completada. Shape final: {df.shape}")

        # Convertir columnas de tipo lista/dict a string para que SQLite las acepte
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                self.log.info(f"[Listings] Convirtiendo columna compleja '{col}' a string para carga.")
                df[col] = df[col].astype(str)
        return df

    # ── Transformacion de Reviews ──────────────────────────────────────────────

    def transformar_reviews(self) -> pd.DataFrame:
        """
        Aplica el pipeline completo de transformacion sobre el DataFrame de reviews.

        Transformaciones aplicadas:
          1. Limpieza de duplicados.
          2. Conversion de la columna 'date' a fecha estandar con derivadas.
          3. Relleno de nulos en columna 'comments' con texto indicativo.
          4. Estandarizacion de texto en columna 'reviewer_name'.

        Returns:
            pd.DataFrame: DataFrame de reviews transformado y listo para carga.
        """
        self.log.info("Iniciando transformacion de Reviews.")
        df = self.df_reviews.copy()

        # 1. Limpiar duplicados
        df = self._limpiar_nulos_y_duplicados(df, "Reviews")

        # 2. Convertir columna de fecha
        df = self._convertir_fecha(df, "date", "Reviews")

        # 3. Rellenar nulos en comments
        if "comments" in df.columns:
            nulos_comments = df["comments"].isna().sum()
            df["comments"] = df["comments"].fillna("Sin comentario")
            if nulos_comments > 0:
                self.log.warning(
                    f"[Reviews] {nulos_comments:,} nulos en 'comments' reemplazados por 'Sin comentario'."
                )

        # 4. Estandarizar nombre del reviewer
        if "reviewer_name" in df.columns:
            df["reviewer_name"] = df["reviewer_name"].astype(str).str.strip().str.title()

        self.log.info(f"[Reviews] Transformacion completada. Shape final: {df.shape}")
        return df

    # ── Transformacion de Calendar ─────────────────────────────────────────────

    def transformar_calendar(self) -> pd.DataFrame:
        """
        Aplica el pipeline completo de transformacion sobre el DataFrame de calendar.

        Transformaciones aplicadas:
          1. Limpieza de duplicados.
          2. Conversion de la columna 'date' a fecha estandar con derivadas (anio, mes, dia, trimestre).

        Returns:
            pd.DataFrame: DataFrame de calendar transformado y listo para carga.
        """
        self.log.info("Iniciando transformacion de Calendar.")
        df = self.df_calendar.copy()

        # 1. Limpiar duplicados
        df = self._limpiar_nulos_y_duplicados(df, "Calendar")

        # 2. Convertir fecha con derivadas (anio, mes, dia, trimestre)
        df = self._convertir_fecha(df, "date", "Calendar")

        # 3. Normalizar el campo price en Calendar
        if "price" in df.columns:
            df["price"] = df["price"].apply(self._normalizar_precio)
            nulos_price = df["price"].isna().sum()
            self.log.info(f"[Calendar] 'price' convertido a float. Nulos resultantes: {nulos_price:,}")

        self.log.info(f"[Calendar] Transformacion completada. Shape final: {df.shape}")
        return df

    # ── Pipeline completo ──────────────────────────────────────────────────────

    def transformar_todo(self) -> tuple:
        """
        Ejecuta el pipeline completo de transformacion sobre los tres DataFrames.

        Returns:
            tuple: (df_listings_limpio, df_reviews_limpio, df_calendar_limpio)
        """
        self.log.info("Iniciando pipeline completo de transformaciones.")
        df_listings_limpio  = self.transformar_listings()
        df_reviews_limpio   = self.transformar_reviews()
        df_calendar_limpio  = self.transformar_calendar()
        self.log.info("Pipeline de transformaciones finalizado correctamente.")
        return df_listings_limpio, df_reviews_limpio, df_calendar_limpio


# ── Ejecucion directa ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    from extraccion import Extraccion

    ext = Extraccion()
    df_l, df_r, df_c = ext.extraer_todo()
    ext.cerrar_conexion()

    trans = Transformacion(df_l, df_r, df_c)
    df_listings_ok, df_reviews_ok, df_calendar_ok = trans.transformar_todo()

    print("\n--- Listings transformados (primeras filas) ---")
    print(df_listings_ok.head(3))
    print("\n--- Reviews transformados (primeras filas) ---")
    print(df_reviews_ok.head(3))
    print("\n--- Calendar transformados (primeras filas) ---")
    print(df_calendar_ok.head(3))
