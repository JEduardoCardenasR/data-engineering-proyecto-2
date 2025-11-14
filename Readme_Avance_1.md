# Avance 1: Sistema ETL para Carga de Datos a PostgreSQL

## 📋 Descripción General

Este proyecto implementa un sistema ETL (Extract, Transform, Load) completo para cargar datos desde archivos CSV a una base de datos PostgreSQL. El sistema utiliza **arquitectura de staging** (área de preparación) siguiendo las mejores prácticas de Data Engineering:

1. **Carga datos crudos** a tablas staging (sin IDs, sin foreign keys)
2. **Aplica transformaciones** sobre los datos en staging
3. **Carga datos transformados** a producción (con IDs autoincrementales y foreign keys)

El sistema utiliza SQLAlchemy ORM para la definición de esquemas de producción, SQL directo para staging, y pandas para el procesamiento de datos, aplicando patrones de diseño como Singleton para la gestión de conexiones y configuración centralizada.

### Características Principales

- **Arquitectura de Staging**: Separación entre datos crudos y datos transformados
- **Patrón Singleton**: Gestión única de conexión a base de datos mediante `DBConnector`
- **SQLAlchemy ORM**: Definición de modelos de datos para producción
- **SQL Directo**: Creación de tablas staging sin restricciones de ORM
- **Transformaciones Automáticas**: Limpieza y normalización de datos basadas en EDA
- **Resolución Automática de Foreign Keys**: Mapeo automático de IDs durante la carga
- **Configuración Centralizada**: Todos los parámetros configurables en un solo lugar
- **Path Manager**: Gestión centralizada de rutas del proyecto con caché
- **Limpieza Automática**: Estandarización de nombres de columnas (camelCase → snake_case)
- **Carga Optimizada**: Uso de COPY nativo de PostgreSQL para máxima eficiencia

### Estructura del Proyecto

```
Proyecto Integrador/
├── pipeline/                    # Módulo principal del ETL
│   ├── models/                  # Modelos ORM y creación de tablas
│   │   ├── __init__.py
│   │   ├── models.py            # Modelos ORM de producción (11 tablas)
│   │   ├── enums.py             # Enumeraciones para estados
│   │   ├── create_tables.py     # Creación de tablas (staging y producción)
│   │   └── create_staging_tables.sql  # SQL para crear tablas staging
│   │
│   ├── etl/                     # Módulo ETL
│   │   ├── __init__.py
│   │   ├── load_raw_data.py     # Carga datos crudos a staging
│   │   ├── transformations.py   # Transformaciones sobre staging
│   │   ├── load_to_production.py # Carga a producción y resuelve FKs
│   │   └── pipeline.py          # Pipeline modular (ejecución por pasos)
│   │
│   ├── utils/                   # Módulo de utilidades
│   │   ├── __init__.py
│   │   ├── path_manager.py      # Gestión de paths (Singleton)
│   │   ├── config.py            # Configuración centralizada
│   │   └── clean_column_name.py # Estandarización de nombres
│   │
│   ├── scripts/                  # Scripts ejecutables
│   │   └── main.py              # Orquestador principal del ETL
│   │
│   ├── notebooks/               # Notebooks de análisis
│   │   ├── EDA/                 # Análisis exploratorio de datos
│   │   ├── proceso_carga_datos.ipynb
│   │   └── ...
│   │
│   └── __init__.py              # Paquete pipeline
│
├── database/                     # Conexión a base de datos
│   └── db_connector.py          # DBConnector (Singleton)
│
├── data/                         # Datos del proyecto
│   ├── CSV/                     # Archivos CSV originales
│   └── sql/                     # Scripts SQL
│
└── Readme_Avance_1.md           # Este archivo
```

---

## 🔧 Fase 1: Configuración Inicial del Entorno

### Objetivo

Configurar el entorno de trabajo completo para el proyecto, incluyendo entorno virtual, dependencias y conexión a PostgreSQL.

### Componentes Implementados

#### 1. Entorno Virtual y Dependencias

- Entorno virtual de Python (`venv`)
- Archivo `requirements.txt` con dependencias:
  - `psycopg2-binary` (2.9.11) - Driver PostgreSQL
  - `SQLAlchemy` (2.0.44) - ORM
  - `pandas` (2.3.3) - Procesamiento de datos
  - `python-dotenv` (1.2.1) - Variables de entorno

#### 2. DBConnector (Patrón Singleton)

**Ubicación**: `database/db_connector.py`

- Implementación del patrón Singleton para conexión única
- Carga automática de variables de entorno desde `.env`
- Creación y gestión del Engine de SQLAlchemy
- Pool pre-ping para verificación de conexión

**Uso**:
```python
from database.db_connector import DBConnector

db = DBConnector.get_instance()
engine = db.get_engine()
```

#### 3. Variables de Entorno

Archivo `.env` en la raíz del proyecto:
```env
DB_HOST=******
DB_PORT=******
DB_NAME=******
DB_USER=******
DB_PASS=******
```

### Comandos de Configuración

**Windows PowerShell**:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux/Mac**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Estado de la Fase 1

- [x] Entorno virtual creado
- [x] Dependencias instaladas
- [x] Archivo `.env` configurado
- [x] Clase `DBConnector` implementada con patrón Singleton
- [x] Integración con SQLAlchemy configurada

---

## 📊 Fase 2: Refactorización a Arquitectura de Staging

### Objetivo

Refactorizar el proceso ETL para implementar una arquitectura de staging que siga las mejores prácticas de Data Engineering:
- Cargar datos crudos sin IDs ni foreign keys
- Aplicar transformaciones sobre staging
- Cargar datos transformados a producción con generación automática de IDs

### Flujo del Proceso ETL (6 Pasos)

```
1. Crear tablas STAGING (SQL directo, sin IDs, sin FKs)
   ↓
2. Cargar datos CRUDOS a staging (desde CSV)
   ↓
3. Crear tablas de PRODUCCIÓN (ORM, con IDs, FKs, constraints)
   ↓
4. Aplicar TRANSFORMACIONES sobre staging
   ↓
5. Cargar datos TRANSFORMADOS a producción (con generación de IDs)
   ↓
6. Resolver FOREIGN KEYS automáticamente
```

### Componentes Implementados

#### 1. Modelos ORM de Producción (`pipeline/models/models.py`)

Definición de 11 modelos de datos usando SQLAlchemy ORM para la capa de producción:

- `Usuario` - Información de usuarios
- `Categoria` - Categorías de productos
- `Producto` - Catálogo de productos
- `Orden` - Órdenes de compra
- `DetalleOrden` - Detalles de cada orden
- `DireccionEnvio` - Direcciones de envío
- `Carrito` - Carrito de compras
- `MetodoPago` - Métodos de pago disponibles
- `OrdenMetodoPago` - Relación orden-método de pago
- `ResenaProducto` - Reseñas de productos
- `HistorialPago` - Historial de pagos

**Características**:
- Claves primarias auto-incrementales
- Foreign keys para relaciones entre tablas
- Constraints y validaciones (CheckConstraint)
- Enums para campos de estado
- Valores por defecto (server_default)

##### 1.1. Validaciones con CheckConstraint

Se implementaron validaciones numéricas a nivel de base de datos para preservar la integridad semántica:

**Validaciones de valores no negativos**:

| Tabla | Campo | Validación | Constraint |
|-------|-------|------------|------------|
| `productos` | `precio` | `>= 0` | `check_precio_positivo` |
| `productos` | `stock` | `>= 0` | `check_stock_positivo` |
| `ordenes` | `total` | `>= 0` | `check_total_positivo` |
| `detalle_ordenes` | `cantidad` | `>= 0` | `check_cantidad_positiva` |
| `detalle_ordenes` | `precio_unitario` | `>= 0` | `check_precio_unitario_positivo` |
| `carrito` | `cantidad` | `>= 0` | `check_cantidad_carrito_positiva` |
| `ordenes_metodos_pago` | `monto_pagado` | `>= 0` | `check_monto_pagado_positivo` |
| `historial_pagos` | `monto` | `>= 0` | `check_monto_positivo` |
| `resenas_productos` | `calificacion` | `1-5` | `check_calificacion_rango` |

**Total**: 9 validaciones de integridad semántica implementadas.

##### 1.2. Enums para Campos de Estado

Se implementaron Enums nativos de PostgreSQL para campos de estado:

**Archivo**: `pipeline/models/enums.py`

**EstadoOrden** (tabla `ordenes`):
- `PENDIENTE = 'Pendiente'` (valor por defecto)
- `ENVIADO = 'Enviado'`
- `COMPLETADO = 'Completado'`
- `CANCELADO = 'Cancelado'`

**EstadoPago** (tabla `historial_pagos`):
- `PROCESANDO = 'Procesando'` (valor por defecto)
- `PAGADO = 'Pagado'`
- `FALLIDO = 'Fallido'`
- `REEMBOLSADO = 'Reembolsado'`

**Beneficios de los Enums**:
- Validación a nivel de base de datos: PostgreSQL solo acepta valores válidos
- Integridad semántica: previene valores inválidos
- Mejor rendimiento: tipos ENUM nativos son más eficientes que VARCHAR
- Documentación explícita: valores permitidos están claramente definidos en el código

#### 2. Creación de Tablas (`pipeline/models/create_tables.py`)

**Funciones implementadas**:

- `create_staging_tables()`: Crea tablas staging usando SQL directo desde `create_staging_tables.sql`
  - Tablas sin primary keys ni foreign keys
  - Solo almacenan datos crudos tal como vienen del CSV
  - Ejemplo: `usuarios_raw`, `productos_raw`, `ordenes_raw`

- `create_production_tables()`: Crea tablas de producción usando SQLAlchemy ORM
  - Tablas con IDs autoincrementales, foreign keys y constraints
  - Utiliza los modelos definidos en `models.py`

- `create_all_tables()`: Crea ambas capas (staging y producción)

**Archivo SQL**: `pipeline/models/create_staging_tables.sql`
- Define el esquema de todas las tablas staging
- Sin primary keys ni foreign keys
- Permite análisis exploratorio sin restricciones

#### 3. Carga de Datos Crudos a Staging (`pipeline/etl/load_raw_data.py`)

**Función**: `load_raw_data(file_name, table_name_raw)`

**Características**:
- Lee archivos CSV desde `data/CSV/`
- Estandariza nombres de columnas (camelCase → snake_case)
- Filtra columnas automáticamente (excluye IDs primarios si existen en CSV)
- Inserta datos usando el comando **COPY nativo de PostgreSQL** vía `psycopg2` para máxima eficiencia
- Carga datos CRUDOS sin validaciones ni constraints

**Ventajas de COPY**:
- **Máxima eficiencia**: COPY es el método más rápido para cargar datos en PostgreSQL
- **Procesamiento directo**: Los datos se cargan directamente desde memoria sin archivos temporales
- **Transaccional**: Los datos se cargan en una transacción única (todo o nada)

#### 4. Transformaciones (`pipeline/etl/transformations.py`)

**Función principal**: `apply_transformations(table_name_raw, df, **kwargs)`

**Transformaciones aplicadas por tabla**:

| Tabla | Transformaciones | Resultado |
|-------|------------------|-----------|
| `usuarios_raw` | Normalización de emails, trim | 379 emails normalizados |
| `categorias_raw` | Trim de nombre y descripción | - |
| `productos_raw` | Trim, validación de precios y stock (no negativos) | - |
| `ordenes_raw` | Cálculo de totales desde detalle_ordenes | 1,000 totales corregidos |
| `detalle_ordenes_raw` | Validación de cantidades y precios (no negativos) | - |
| `resenas_productos_raw` | Eliminación de duplicados por (usuario_id, producto_id) | 698 reseñas duplicadas eliminadas |
| `direcciones_envio_raw` | Trim de todos los campos de texto | - |
| `carrito_raw` | Validación de cantidades (no negativas) | - |
| `metodos_pago_raw` | Trim de nombre y descripción | - |
| `ordenes_metodos_pago_raw` | Validación de montos (no negativos) | - |
| `historial_pagos_raw` | Validación de montos (no negativos) | - |

**Funciones genéricas**:
- `apply_trim()`: Elimina espacios al inicio y final de campos de texto
- `normalize_emails()`: Normaliza emails (elimina espacios, acentos, caracteres especiales)
- `remove_duplicates_by_key()`: Elimina duplicados basándose en columnas clave

#### 5. Carga a Producción (`pipeline/etl/load_to_production.py`)

**Función principal**: `load_all_to_production()`

**Características**:
- Lee datos transformados desde tablas staging
- Genera IDs autoincrementales automáticamente
- Resuelve foreign keys usando mapeos de identificadores naturales
- Respeta orden de dependencias (tablas independientes primero)

**Orden de carga** (respetando dependencias):
1. **Nivel 1** (independientes): `categorias`, `metodos_pago`, `usuarios`
2. **Nivel 2** (dependen de nivel 1): `productos`, `ordenes`
3. **Nivel 3** (dependen de nivel 2): `detalle_ordenes`, `carrito`, `direcciones_envio`, `resenas_productos`, `ordenes_metodos_pago`, `historial_pagos`

**Mapeo de IDs**:
- Usa identificadores naturales (nombre, dni, email) para crear mapeos
- Convierte referencias de staging a IDs de producción automáticamente
- Ejemplo: `{'nombre': 1, 'nombre2': 2}` para categorias

#### 6. Pipeline Modular (`pipeline/etl/pipeline.py`)

**Funciones disponibles**:

- `run_full_pipeline()`: Ejecuta todo el proceso ETL completo
- `run_staging_load()`: Solo carga datos crudos a staging
- `run_transformations()`: Solo aplica transformaciones sobre staging
- `run_production_load()`: Solo carga datos transformados a producción

**Útil para**:
- Desarrollo incremental
- Debugging
- Mantenimiento
- Reprocesamiento selectivo

#### 7. Estandarización de Nombres (`pipeline/utils/clean_column_name.py`)

**Función**: `clean_column_name()`

- Convierte camelCase a snake_case (ej: `OrdenID` → `orden_id`)
- Convierte a minúsculas
- Maneja transiciones de mayúsculas/minúsculas
- Elimina caracteres especiales

#### 8. Configuración Centralizada (`pipeline/utils/config.py`)

**Clase**: `ETLConfig`

**Parámetros configurables**:
- Paths de directorios: `CSV_DIR = 'data/CSV'`, `SQL_DIR = 'data/sql'`
- Encoding: `CSV_ENCODING = 'utf-8'`

#### 9. Path Manager (`pipeline/utils/path_manager.py`)

**Clase**: `PathManager` (Singleton)

- Gestiona paths del proyecto de manera centralizada
- Evita duplicación de código
- Implementa caché para evitar recálculos
- Configura `sys.path` para imports

#### 10. Orquestador Principal (`pipeline/scripts/main.py`)

**Función**: `main()`

**Flujo completo**:
1. Crear tablas staging
2. Cargar datos crudos a staging
3. Crear tablas de producción
4. Ejecutar transformaciones sobre staging
5. Cargar datos transformados a producción (con generación de IDs)
6. Resolver foreign keys (automático)

### Archivos CSV Procesados

| Archivo | Tabla Staging | Tabla Producción | Filas |
|---------|---------------|------------------|-------|
| `2.Usuarios.csv` | `usuarios_raw` | `usuarios` | 1,000 |
| `3.Categorias.csv` | `categorias_raw` | `categorias` | 12 |
| `4.Productos.csv` | `productos_raw` | `productos` | 36 |
| `5.ordenes.csv` | `ordenes_raw` | `ordenes` | 10,000 |
| `6.detalle_ordenes.csv` | `detalle_ordenes_raw` | `detalle_ordenes` | 10,000 |
| `7.direcciones_envio.csv` | `direcciones_envio_raw` | `direcciones_envio` | 1,000 |
| `8.carrito.csv` | `carrito_raw` | `carrito` | 5,000 |
| `9.metodos_pago.csv` | `metodos_pago_raw` | `metodos_pago` | 7 |
| `10.ordenes_metodospago.csv` | `ordenes_metodos_pago_raw` | `ordenes_metodos_pago` | 10,000 |
| `11.resenas_productos.csv` | `resenas_productos_raw` | `resenas_productos` | 6,474* |
| `12.historial_pagos.csv` | `historial_pagos_raw` | `historial_pagos` | 10,000 |

*Después de eliminar 698 reseñas duplicadas

**Total**: 
- 55,227 registros cargados a staging (datos crudos)
- 64,474 registros transformados
- 64,474 registros cargados a producción (con IDs autoincrementales)

### Ejecución del Proceso ETL

**Opción 1: Script principal**:
```bash
# Desde la raíz del proyecto
python pipeline/scripts/main.py

# O como módulo
python -m pipeline.scripts.main
```

**Opción 2: Pipeline modular**:
```python
from pipeline.etl.pipeline import run_full_pipeline

# Ejecutar todo el proceso
id_mappings = run_full_pipeline()

# O ejecutar por pasos
from pipeline.etl.pipeline import (
    run_staging_load,
    run_transformations,
    run_production_load
)

run_staging_load()
staging_data = run_transformations()
id_mappings = run_production_load()
```

### Flujo del Proceso Detallado

```
pipeline/scripts/main.py
  │
  ├─→ Paso 1: models.create_staging_tables()
  │   └─→ Lee create_staging_tables.sql y ejecuta SQL directo
  │       └─→ Crea 11 tablas staging (sin IDs, sin FKs)
  │
  ├─→ Paso 2: etl.load_raw_data() para cada CSV
  │   ├─→ Lee CSV con pandas (usa utils.path_manager)
  │   ├─→ Limpia nombres de columnas (usa utils.clean_column_name)
  │   ├─→ Filtra columnas (excluye IDs primarios)
  │   └─→ Inserta datos en staging usando COPY (máxima eficiencia)
  │
  ├─→ Paso 3: models.create_production_tables()
  │   └─→ Crea 11 tablas de producción usando ORM
  │       └─→ Con IDs autoincrementales, FKs y constraints
  │
  ├─→ Paso 4: etl.transformations.apply_transformations()
  │   ├─→ Lee datos de staging
  │   ├─→ Aplica transformaciones específicas por tabla
  │   └─→ Actualiza staging con datos transformados
  │
  └─→ Paso 5-6: etl.load_to_production.load_all_to_production()
      ├─→ Lee datos transformados de staging
      ├─→ Genera IDs autoincrementales
      ├─→ Resuelve foreign keys usando mapeos
      └─→ Inserta datos en producción
```

### Estado de la Fase 2

- [x] Arquitectura de staging implementada
- [x] Modelos ORM de producción definidos (11 tablas)
- [x] Tablas staging creadas con SQL directo
- [x] Función de carga de datos crudos a staging implementada
- [x] Módulo de transformaciones implementado
- [x] Función de carga a producción con resolución de FKs implementada
- [x] Pipeline modular implementado
- [x] Estandarización de nombres de columnas
- [x] Configuración centralizada
- [x] Path Manager implementado
- [x] Orquestador principal funcional
- [x] Proceso ETL completo probado
- [x] Validaciones numéricas con CheckConstraint (9 validaciones)
- [x] Enums para campos de estado (EstadoOrden, EstadoPago)
- [x] Resolución automática de foreign keys
- [x] Mapeo de IDs usando identificadores naturales

---

## 🎯 Patrones de Diseño Aplicados

1. **Singleton**: `DBConnector` y `PathManager` para instancias únicas
2. **Configuración Centralizada**: `ETLConfig` para valores configurables
3. **Separación de Responsabilidades**: Organización modular por función
   - `models/`: Modelos ORM, enumeraciones y creación de esquema
   - `etl/`: Proceso de carga de datos desde CSV (con staging)
   - `utils/`: Utilidades compartidas (paths, configuración, transformaciones)
   - `scripts/`: Scripts ejecutables
4. **Arquitectura de Capas**: Separación entre staging (raw) y producción (transformada)

---

## 🔄 Ventajas del Nuevo Flujo con Staging

1. **Separación de responsabilidades**: Datos crudos vs datos transformados
2. **Análisis exploratorio**: Puedes analizar datos crudos sin restricciones
3. **Reprocesamiento**: Fácil reprocesar si hay errores
4. **Trazabilidad**: Puedes comparar staging vs producción
5. **Mejores prácticas**: Sigue el patrón estándar de Data Warehousing
6. **Flexibilidad**: Permite ejecutar el pipeline por pasos
7. **Debugging**: Facilita identificar problemas en cada etapa

---

## 📚 Referencias

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Patrón Singleton en Python](https://refactoring.guru/design-patterns/singleton/python/example)
- [Data Warehousing Best Practices](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/)

---

**Fecha de Documentación**: Enero 2025  
**Versión**: 3.0 - Refactorización a Arquitectura de Staging Completada
