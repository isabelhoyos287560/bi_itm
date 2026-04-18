# ETL Airbnb — Ciudad Autónoma de Buenos Aires

## Descripción general

Proyecto académico de un pipeline ETL (Extract, Transform, Load) profesional sobre datasets de Airbnb (México) con mongodb, aplicando transformaciones complejas de datos, validación de integridad y exportación dual a SQLite y XLSX.

El proyecto implementa un sistema robusto de extracción desde MongoDB, aplica transformaciones avanzadas de limpieza, normalización, categorización y enriquecimiento de datos, y carga el resultado en una base de datos SQLite con exportación automática a archivos Excel. Incluye sistema de logging granular con trazabilidad completa.

## Objetivo

Aplicar los conceptos de Extracción, Transformación y Carga (ETL) sobre datasets de Airbnb mediante un pipeline automatizado que demuestre:
- Integración con bases de datos NoSQL (MongoDB)
- Transformaciones complejas de limpieza y estandarización
- Validación de integridad de datos
- Logging granular y trazabilidad
- Exportación a múltiples formatos (SQLite, XLSX)

## Estructura del repositorio

```
entrega3/
├── src/
│   ├── logger.py              # Clase reutilizable de manejo de logs con archivos por módulo
│   ├── config.py              # Configuración centralizada y gestión de variables de entorno
│   ├── extraccion.py          # Clase Extraccion — conexión a MongoDB y lectura de colecciones
│   ├── transformacion.py      # Clase Transformacion — pipeline completo de limpieza y enriquecimiento
│   ├── carga.py               # Clase Carga — inserción en SQLite y exportación XLSX
│   ├── main.py                # Script principal que orquesta el ETL
│   └── data/
│       ├── etl_airbnb_mexico.db    # 📁 GENERADO: Base de datos SQLite
│       └── processed/              # 📁 GENERADO: Exportaciones XLSX
├── notebooks/
│   ├── exploracion_airbnb.ipynb    # Análisis exploratorio de datos (EDA)
│   └── logs/                       # Logs de extracción del notebook
├── logs/                      # Logs generados por cada ejecución del ETL
├── .env.example               # Plantilla de variables de entorno (MongoDB)
├── requirements.txt           # Dependencias del proyecto
└── README.md
```

**Nota:** Los archivos generados (DB SQLite, XLSX, logs) se ignoran en Git por superar límites de almacenamiento.

## Prerrequisitos

- **Python 3.10+**
- **MongoDB local** corriendo en `localhost:27017` (o URL configurable vía `.env`)
- **Colecciones de datos** preimportadas en MongoDB:
  - Base de datos: `airbnb_itm`
  - Colecciones: `Listings_mexico`, `Reviews_mexico`, `Calendar_mexico`

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd etl_airbnb/entrega3
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

Dependencias principales:
- `pandas`: Manipulación de DataFrames
- `pymongo`: Conexión a MongoDB
- `openpyxl`: Exportación a Excel
- `python-dotenv`: Carga de variables de entorno

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con los parámetros reales de MongoDB
```

**Contenido de `.env`:**
```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=airbnb_itm
MONGO_COLLECTION_LISTINGS=Listings_mexico
MONGO_COLLECTION_REVIEWS=Reviews_mexico
MONGO_COLLECTION_CALENDAR=Calendar_mexico
MONGO_TIMEOUT=5000
```

## Carga de datos en MongoDB

Los datos deben estar preimportados en MongoDB antes de ejecutar el ETL:

1. **MongoDB ejecutándose** en `localhost:27017` (o URL especificada en `.env`)
2. **Base de datos `airbnb_itm`** creada
3. **Colecciones pobladas**:
   - `Listings_mexico`: Datos de propiedades
   - `Reviews_mexico`: Reseñas de huéspedes
   - `Calendar_mexico`: Disponibilidad y precios diarios

### Importar datos JSON a MongoDB

```bash
# Importar colección Listings
mongoimport --db airbnb_itm --collection Listings_mexico --file listings.json --jsonArray

# Importar colección Reviews
mongoimport --db airbnb_itm --collection Reviews_mexico --file reviews.json --jsonArray

# Importar colección Calendar
mongoimport --db airbnb_itm --collection Calendar_mexico --file calendar.json --jsonArray
```

## Ejecución del proyecto

### Ejecutar el ETL completo

```bash
python src/main.py
```

Este comando ejecuta automáticamente las **3 fases en orden**:
1. **Extracción** desde MongoDB → DataFrames
2. **Transformación** con limpieza y enriquecimiento
3. **Carga** en SQLite y exportación XLSX

### Ejecutar módulos individuales (debug/testing)

```bash
# Solo extracción (valida conexión a MongoDB)
python src/extraccion.py

# Solo transformación (requiere DataFrames previos)
python src/transformacion.py

# Solo carga (requiere datos transformados previos)
python src/carga.py
```

## Sistema de Logs

### Estructura de logs

Se generan 4 archivos de log por ejecución en la carpeta `logs/`:

```
logs/
├── log_main_YYYYMMDD_HHMM.txt          # Ejecución general del pipeline
├── log_extraccion_YYYYMMDD_HHMM.txt    # Conexión y lectura de MongoDB
├── log_transformacion_YYYYMMDD_HHMM.txt # Limpieza y transformaciones
└── log_carga_YYYYMMDD_HHMM.txt         # Inserción en SQLite y XLSX
```

### Características

- 🔄 **Doble salida**: Simultáneamente a archivo y consola
- 📊 **3 niveles de severidad**: INFO, WARNING, ERROR
- ⏰ **Timestamps uniformes**: YYYY-MM-DD HH:MM:SS
- 🛡️ **Prevención de duplicados**: Evita handlers repetidos
- 📁 **Directorio automático**: Crea `logs/` si no existe

### Ejemplo de log

```
2026-04-18 14:35:22 - INFO - Iniciando extracción de MongoDB
2026-04-18 14:35:23 - INFO - Conectando a MongoDB: mongodb://localhost:27017
2026-04-18 14:35:24 - INFO - Extrayendo colección Listings_mexico...
2026-04-18 14:35:28 - INFO - Se extrajo 1250 registros de Listings
2026-04-18 14:35:45 - INFO - Extracción completada exitosamente
```



# Detalles de los módulos

## 1. Logger (`logger.py`)

**Clase personalizada de logging** con características avanzadas:

- 📁 **Logs persistentes**: Un archivo por ejecución con formato `log_MÓDULO_YYYYMMDD_HHMM.txt`
- 🔄 **Doble salida**: Simultáneamente a archivo y consola
- 📊 **Niveles de log**: INFO, WARNING, ERROR
- 🛡️ **Prevención de duplicados**: Control de handlers para evitar repeticiones
- ⏰ **Timestamps uniformes**: YYYY-MM-DD HH:MM:SS

## 2. Config (`config.py`)

**Gestión centralizada de configuración**:

- 📋 Lee variables de entorno desde `.env` usando `python-dotenv`
- 🔐 Parámetros configurables:
  - URI de MongoDB con timeout personalizado (5000ms por defecto)
  - Base de datos `airbnb_itm`
  - Colecciones: `Listings_mexico`, `Reviews_mexico`, `Calendar_mexico`
  - Rutas del proyecto (data, processed, logs)

## 3. Extracción (`extraccion.py`)

**Clase `Extraccion`**: Conexión a MongoDB y lectura de datos

### Características

- 🔐 **Conexión segura**: Manejo de `ConnectionFailure` y `ServerSelectionTimeoutError`
- ✅ **Validación**: Ping a MongoDB para asegurar conexión real
- 📊 **Métodos granulares**: `extraer_listings()`, `extraer_reviews()`, `extraer_calendar()`
- 📝 **Logging detallado**: Registra URI, colecciones, conteos de registros
- 🧹 **Limpieza**: Excluye `_id` de MongoDB en la conversión a DataFrame
- 🛡️ **Manejo de errores**: DataFrames vacíos en caso de fallos

### Salida

```
listings: 1250 registros x 74 columnas
reviews: 5430 registros x 6 columnas
calendar: 12000 registros x 7 columnas
```

## 4. Transformación (`transformacion.py`)

**Clase `Transformacion`**: Pipeline completo de limpieza, normalización y enriquecimiento

### A. Limpieza de datos

- ✅ **Eliminación de duplicados**: Detecta y elimina registros duplicados
- ✅ **Manejo de nulos**: Rellena valores críticos (ej: nombres, comentarios)

### B. Normalización de precios

Conversión de formato moneda → número:
```
"$1,200.00" → 1200.0
```

Campos procesados: `price`, `weekly_price`, `monthly_price`, `security_deposit`, `cleaning_fee`

### C. Procesamiento de fechas

Conversión a formato estándar `YYYY-MM-DD` con derivación de variables temporales:

| Variable | Descripción |
|---|---|
| `date`, `last_scraped` | Fecha original |
| `_anio` | Año extraído |
| `_mes` | Mes extraído |
| `_dia` | Día extraído |
| `_trimestre` | Trimestre (Q1, Q2, Q3, Q4) |

### D. Categorización de precios

Clasificación automática por rango:

```
Económico:    ≤ $50
Moderado:     $50 - $150
Alto:         $150 - $300
Premium:      > $300
```

### E. Enriquecimiento (Listings)

- 🎯 **Conteo de amenities**: Convierte campo anidado → cantidad numérica
  ```
  ['wifi', 'tv', 'cocina'] → 3
  ```
- 🎯 **Estandarización de texto**: `.strip().title()` en nombre, tipo, categoría, barrio
- 🎯 **Conversión de tipos complejos**: Listas/dicts → string (para compatibilidad SQLite)

### F. Procesamiento de Reviews

- 💬 Relleno de comentarios vacíos con "Sin comentario"
- 💬 Estandarización de nombres de reviewers

### G. Procesamiento de Calendar

- 📆 Limpieza y conversión de fechas
- 📆 Normalización de precios diarios

## 5. Carga (`carga.py`)

**Clase `Carga`**: Inserción en SQLite y exportación a XLSX

### A. Inserción en SQLite

- 🗄️ Crea 3 tablas: `listings`, `reviews`, `calendar`
- 🔄 Estrategia `replace` permite reruns sin conflictos
- 📊 Registra conteo de registros cargados
- ✔️ Verifica integridad: valida existencia de tablas y conteos exactos

### B. Exportación a XLSX

Genera 3 archivos Excel en `src/data/processed/`:

```
listings_transformado.xlsx     (1250 registros)
reviews_transformado.xlsx      (5430 registros)
calendar_transformado.xlsx     (12000 registros)
```

Usa `openpyxl` como motor de exportación.

## 6. Main (`main.py`)

**Orquestador del pipeline ETL**

Ejecuta las 3 fases en orden:
1. 🟦 **Extracción**: Lee desde MongoDB
2. 🟩 **Transformación**: Limpia y enriquece datos
3. 🟨 **Carga**: Inserta en SQLite y exporta XLSX

Con logging detallado de inicio y fin del proceso.

---

## Salidas generadas

Al ejecutar `python src/main.py`, se crean automáticamente:

### Base de datos
```
src/data/
└── etl_airbnb_mexico.db       # SQLite con 3 tablas
```

### Exportaciones Excel
```
src/data/processed/
├── listings_transformado.xlsx
├── reviews_transformado.xlsx
└── calendar_transformado.xlsx
```

### Logs (por ejecución)
```
logs/
├── log_main_YYYYMMDD_HHMM.txt
├── log_extraccion_YYYYMMDD_HHMM.txt
├── log_transformacion_YYYYMMDD_HHMM.txt
└── log_carga_YYYYMMDD_HHMM.txt
```

---

## Análisis Exploratorio

### Notebook EDA

Se incluye un Jupyter Notebook con análisis exploratorio de los datos de Airbnb:

```bash
jupyter notebook notebooks/exploracion_airbnb.ipynb
```

Contiene visualizaciones y estadísticas de distribuciones, correlaciones y patrones en los datos.

---

## Características tecnológicas destacadas

| Característica | Beneficio |
|---|---|
| **Sistema de logs modular** | Trazabilidad por fase, fácil debugging |
| **Configuración por `.env`** | Flexibilidad entre ambientes (dev/prod) |
| **Validación post-carga** | Asegura integridad de datos en destino |
| **Exportación dual** | SQLite para análisis, Excel para stakeholders |
| **Derivación de variables temporales** | Facilita análisis por período (mes, trimestre, año) |
| **Manejo de campos anidados** | Conversión inteligente (amenities: lista → número) |
| **Prevención de duplicados** | Estrategia `replace` permite reruns seguros |
| **Type hints y docstrings** | Código autodocumentado y mantenible |
| **Manejo robusto de errores** | Try-except en conexiones y operaciones críticas |

---

## Mejoras futuras

- Caché de datos transformados para évitar reprocesamiento
- Validación de esquema pre-inserción
- Soporte para procesamiento paralelo de grandes volúmenes
- Alertas automáticas ante anomalías en datos
- Historial de cambios (data lineage)

---

## Fuente de datos

Inside Airbnb — México  
[http://insideairbnb.com/get-the-data](http://insideairbnb.com/get-the-data)
