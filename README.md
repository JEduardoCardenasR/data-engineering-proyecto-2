# Avance 1: Sistema ETL para Carga de Datos a PostgreSQL

## 📋 Descripción General

Este proyecto implementa un sistema ETL (Extract, Transform, Load) completo para cargar datos desde archivos CSV a una base de datos PostgreSQL. El sistema utiliza SQLAlchemy ORM para la definición de esquemas y pandas para el procesamiento de datos, aplicando patrones de diseño como Singleton para la gestión de conexiones y configuración centralizada.

### Características Principales

- **Patrón Singleton**: Gestión única de conexión a base de datos mediante `DBConnector`
- **SQLAlchemy ORM**: Definición de modelos de datos y creación automática de esquema
- **Configuración Centralizada**: Todos los parámetros configurables en un solo lugar
- **Path Manager**: Gestión centralizada de rutas del proyecto con caché
- **Limpieza Automática**: Estandarización de nombres de columnas (camelCase → snake_case)
- **Carga Optimizada**: Procesamiento por lotes con chunksize configurable

### Estructura del Proyecto

```
Avance1/
├── Models/                   # Módulo de modelos ORM
│   ├── __init__.py
│   ├── models.py            # Modelos ORM (11 tablas)
│   ├── enums.py             # Enumeraciones para estados
│   └── create_tables.py     # Creación de esquema
│
├── ETL/                     # Módulo ETL
│   ├── __init__.py
│   └── load_data.py         # Carga de datos desde CSV
│
├── Utils/                    # Módulo de utilidades
│   ├── __init__.py
│   ├── path_manager.py      # Gestión de paths (Singleton)
│   ├── config.py            # Configuración centralizada
│   └── clean_column_name.py # Estandarización de nombres
│
├── main.py                   # Orquestador del proceso ETL
├── __init__.py              # Paquete Avance1
└── README.md                # Este archivo
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

**Ubicación**: `Database/db_connector.py`

- Implementación del patrón Singleton para conexión única
- Carga automática de variables de entorno desde `.env`
- Creación y gestión del Engine de SQLAlchemy
- Pool pre-ping para verificación de conexión

**Uso**:
```python
from Database.db_connector import DBConnector

db = DBConnector.get_instance()
engine = db.get_engine()
```

#### 3. Variables de Entorno

Archivo `.env` en la raíz del proyecto:
```env
DB_HOST=******
DB_PORT==******
DB_NAME==******
DB_USER==******
DB_PASS==******
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

## 📊 Fase 2: Carga Inicial de Datos (ETL)

### Objetivo

Implementar el proceso ETL completo para crear el esquema de base de datos y cargar datos desde archivos CSV a PostgreSQL.

### Componentes Implementados

#### 1. Modelos ORM (`Models/models.py`)

Definición de 11 modelos de datos usando SQLAlchemy ORM:

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

Se implementaron Enums nativos de PostgreSQL para campos de estado, extraídos directamente de los archivos CSV:

**Archivo**: `Models/enums.py`

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

**Implementación en modelos**:
```python
# Orden.estado
estado = Column(Enum(EstadoOrden, name='estado_orden', native_enum=True), 
                server_default=EstadoOrden.PENDIENTE.value)

# HistorialPago.estado_pago
estado_pago = Column(Enum(EstadoPago, name='estado_pago', native_enum=True), 
                     server_default=EstadoPago.PROCESANDO.value)
```

#### 2. Creación de Tablas (`Models/create_tables.py`)

Función `create_all_tables()` que:
- Utiliza `Base.metadata.create_all()` de SQLAlchemy
- Crea todas las tablas definidas en los modelos
- Maneja errores y proporciona feedback

#### 3. Carga de Datos (`ETL/load_data.py`)

Función `load_data(file_name, table_name)` que:
- Lee archivos CSV desde `DataSet/CSV/`
- Estandariza nombres de columnas (camelCase → snake_case)
- Inserta datos usando el comando **COPY nativo de PostgreSQL** vía `psycopg2` para máxima eficiencia
- Procesa todos los datos de una vez (COPY es mucho más rápido que INSERT individuales)

**Características de COPY**:
- **Máxima eficiencia**: COPY es el método más rápido para cargar datos en PostgreSQL
- **Procesamiento directo**: Los datos se cargan directamente desde memoria sin archivos temporales
- **Transaccional**: Los datos se cargan en una transacción única (todo o nada)
- `encoding='utf-8'` - Encoding de archivos CSV

#### 4. Estandarización de Nombres (`Utils/clean_column_name.py`)

Función `clean_column_name()` que:
- Convierte camelCase a snake_case (ej: `OrdenID` → `orden_id`)
- Convierte a minúsculas
- Maneja transiciones de mayúsculas/minúsculas
- Elimina caracteres especiales

#### 5. Configuración Centralizada (`Utils/config.py`)

Clase `ETLConfig` con todos los parámetros configurables:
- Paths de directorios (CSV, SQL)
- Parámetros de carga (chunksize, encoding, método)
- Comportamiento de inserción (if_exists)

#### 6. Path Manager (`Utils/path_manager.py`)

Clase `PathManager` (Singleton) que:
- Gestiona paths del proyecto de manera centralizada
- Evita duplicación de código
- Implementa caché para evitar recálculos
- Configura `sys.path` para imports

#### 7. Orquestador Principal (`main.py`)

Función `main()` que:
1. Crea todas las tablas usando `create_all_tables()`
2. Carga datos desde 11 archivos CSV usando `load_data()`
3. Proporciona resumen del proceso

### Archivos CSV Procesados

| Archivo | Tabla | Filas |
|---------|-------|-------|
| `2.Usuarios.csv` | `usuarios` | 1,000 |
| `3.Categorias.csv` | `categorias` | 12 |
| `4.Productos.csv` | `productos` | 36 |
| `5.ordenes.csv` | `ordenes` | 10,000 |
| `6.detalle_ordenes.csv` | `detalle_ordenes` | 10,000 |
| `7.direcciones_envio.csv` | `direcciones_envio` | 1,000 |
| `8.carrito.csv` | `carrito` | 5,000 |
| `9.metodos_pago.csv` | `metodos_pago` | 7 |
| `10.ordenes_metodospago.csv` | `ordenes_metodos_pago` | 10,000 |
| `11.resenas_productos.csv` | `resenas_productos` | 7,172 |
| `12.historial_pagos.csv` | `historial_pagos` | 10,000 |

**Total**: 11 tablas, ~55,227 registros

### Ejecución del Proceso ETL

```bash
# Desde la raíz del proyecto
python Avance1/main.py

# O como módulo
python -m Avance1.main
```

### Flujo del Proceso

```
main.py (Avance1/)
  │
  ├─→ Paso 1: Models.create_all_tables()
  │   └─→ Crea 11 tablas en PostgreSQL usando Models.models
  │
  └─→ Paso 2: ETL.load_data() para cada CSV
      ├─→ Lee CSV con pandas (usa Utils.path_manager)
      ├─→ Limpia nombres de columnas (usa Utils.clean_column_name)
      └─→ Inserta datos en PostgreSQL (usa Utils.config)
```

### Estado de la Fase 2

- [x] Modelos ORM definidos (11 tablas)
- [x] Función de creación de tablas implementada
- [x] Función de carga de datos implementada
- [x] Estandarización de nombres de columnas
- [x] Configuración centralizada
- [x] Path Manager implementado
- [x] Orquestador principal funcional
- [x] Proceso ETL completo probado
- [x] Validaciones numéricas con CheckConstraint (9 validaciones)
- [x] Enums para campos de estado (EstadoOrden, EstadoPago)

---

## 🎯 Patrones de Diseño Aplicados

1. **Singleton**: `DBConnector` y `PathManager` para instancias únicas
2. **Configuración Centralizada**: `ETLConfig` para valores configurables
3. **Separación de Responsabilidades**: Organización modular por función
   - `Models/`: Modelos ORM, enumeraciones y creación de esquema
   - `ETL/`: Proceso de carga de datos desde CSV
   - `Utils/`: Utilidades compartidas (paths, configuración, transformaciones)

---

## 📚 Referencias

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Patrón Singleton en Python](https://refactoring.guru/design-patterns/singleton/python/example)

---

**Fecha de Documentación**: Enero 2025  
**Versión**: 2.0 - Fases 1 y 2 Completadas