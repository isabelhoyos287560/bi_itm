# ETL Airbnb — Ciudad Autónoma de Buenos Aires

## Descripción general

Proyecto académico del proceso ETL (Extract, Transform, Load) sobre los datasets de Airbnb de Buenos Aires, Argentina. El proyecto extrae datos desde MongoDB, aplica transformaciones de calidad y estandarización, y carga el resultado en SQLite con exportación a XLSX.

## Objetivo

Aplicar los conceptos de Extracción, Transformación y Carga (ETL) sobre los datasets de Airbnb almacenados en MongoDB, mediante un proceso automatizado en Python con manejo de logs, análisis exploratorio de datos y documentación del flujo de trabajo.

## Estructura del repositorio

```
etl_airbnb/
├── src/
│   ├── logger.py           # Clase reutilizable de manejo de logs
│   ├── config.py           # Configuración central y variables de entorno
│   ├── extraccion.py       # Clase Extraccion — conexión a MongoDB y carga en DataFrames
│   ├── transformacion.py   # Clase Transformacion — limpieza y estandarización
│   ├── carga.py            # Clase Carga — SQLite y exportación XLSX
│   ├── main.py             # Script principal que orquesta el ETL completo
│   └── data/
│       └── processed/      # Salidas transformadas (XLSX y SQLite)
├── notebooks/
│   └── exploracion_airbnb.ipynb   # Análisis exploratorio de datos (EDA)
├── logs/                   # Archivos de log generados por cada ejecución
├── .env.example            # Plantilla de variables de entorno
├── requirements.txt        # Dependencias del proyecto
└── README.md
```

## Prerrequisitos

- Python 3.10+
- MongoDB local corriendo en `localhost:27017`
- Las colecciones `listings`, `reviews` y `calendar` ya importadas en la base de datos `airbnb_buenosaires`

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd etl_airbnb
```

### 2. Crear entorno virtual

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con los datos reales de conexión a MongoDB
```

## Carga de datos en MongoDB

Antes de ejecutar el ETL, importar los datasets a MongoDB:

```bash
# Descomprimir los archivos
gunzip listings.csv.gz
gunzip reviews.csv.gz
gunzip calendar.csv.gz

# Importar a MongoDB
mongoimport --db airbnb_buenosaires --collection listings  --type csv --headerline --file listings.csv
mongoimport --db airbnb_buenosaires --collection reviews   --type csv --headerline --file reviews.csv
mongoimport --db airbnb_buenosaires --collection calendar  --type csv --headerline --file calendar.csv
```

## Ejecución del proyecto

### Ejecutar el ETL completo

```bash
python src/main.py
```

Este comando ejecuta en secuencia: extracción → transformación → carga en SQLite → exportación XLSX.

### Ejecutar módulos individuales

```bash
# Solo extracción (prueba de conexión)
python src/extraccion.py

# Solo transformación
python src/transformacion.py

# Solo carga
python src/carga.py
```

### Abrir el notebook de EDA

```bash
jupyter notebook notebooks/exploracion_airbnb.ipynb
```

## Salidas generadas

| Archivo | Ubicación | Descripción |
|---|---|---|
| `etl_airbnb.db` | `src/data/` | Base SQLite con las tres tablas transformadas |
| `listings_transformado.xlsx` | `src/data/processed/` | Listings listos para análisis |
| `reviews_transformado.xlsx` | `src/data/processed/` | Reviews listos para análisis |
| `calendar_transformado.xlsx` | `src/data/processed/` | Calendar listos para análisis |
| `log_*.txt` | `logs/` | Logs de cada ejecución del proceso |

## Logs

Cada módulo genera un archivo de log con el formato `log_<modulo>_YYYYMMDD_HHMM.txt`. Los logs registran eventos con niveles INFO, WARNING y ERROR, e incluyen fecha, hora y descripción clara del evento.

Ejemplo de log generado:
```
2026-04-04 10:32:01 - INFO    - Logger iniciado para el modulo: extraccion
2026-04-04 10:32:01 - INFO    - Intentando conectar a MongoDB: mongodb://localhost:27017/
2026-04-04 10:32:01 - INFO    - Conexion exitosa a la base de datos: 'airbnb_buenosaires'
2026-04-04 10:32:02 - INFO    - Coleccion 'listings' extraida correctamente. Registros: 22.000 | Columnas: 74
2026-04-04 10:32:05 - INFO    - Coleccion 'reviews' extraida correctamente. Registros: 450.000 | Columnas: 6
2026-04-04 10:32:10 - INFO    - Coleccion 'calendar' extraida correctamente. Registros: 8.030.000 | Columnas: 7
```

## Integrantes del grupo

| Nombre | Responsabilidad |
|---|---|
| [Nombre 1] | Extracción y conexión MongoDB |
| [Nombre 2] | Transformación y EDA |
| [Nombre 3] | Carga SQLite, XLSX e informe |

## Fuente de datos

Inside Airbnb — Buenos Aires, Argentina  
[http://insideairbnb.com/get-the-data](http://insideairbnb.com/get-the-data)
