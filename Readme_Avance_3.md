# Proyecto Integrador - Avance 3: Data Warehouse con dbt

Este documento consolida toda la información del proyecto de Data Engineering para e-commerce, incluyendo el pipeline ETL, modelo dimensional Kimball, transformaciones con dbt, y análisis de datos.

## 📋 Tabla de Contenidos

1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Inicio Rápido](#inicio-rápido)
3. [Proyecto dbt](#proyecto-dbt)
4. [Capas de Transformación](#capas-de-transformación)
5. [Modelo Dimensional](#modelo-dimensional)
6. [Slowly Changing Dimensions (SCD)](#slowly-changing-dimensions-scd)
7. [Modelo Físico (DDL)](#modelo-físico-ddl)
8. [Scripts SQL de Referencia](#scripts-sql-de-referencia)
9. [Integridad Referencial](#integridad-referencial)
10. [Vistas Analíticas y Storytelling](#vistas-analíticas-y-storytelling)
11. [Docker Setup](#docker-setup)
12. [Uso y Comandos](#uso-y-comandos)

---

## Estructura del Proyecto

```
.
├── data/                    # Datos fuente (CSV y SQL)
├── database/                # Conexión a base de datos
├── pipeline/                # Pipeline ETL
│   ├── etl/                 # Scripts ETL
│   ├── models/              # Modelos ORM
│   ├── notebooks/           # Notebooks de análisis
│   └── scripts/             # Scripts principales
├── dbt/                     # Proyecto dbt
│   ├── models/              # Modelos dbt
│   │   ├── staging/         # Modelos de staging (stg_*)
│   │   ├── intermediate/    # Modelos intermedios (int_*)
│   │   ├── marts/           # Modelos finales (marts)
│   │   │   ├── fact/        # Tablas de hechos (fct_*)
│   │   │   └── dimension/   # Tablas de dimensiones (dim_*)
│   │   └── analytics/       # Vistas analíticas (vw_*)
│   ├── snapshots/           # Snapshots para SCD Type 2
│   ├── sql/                 # Scripts DDL del modelo físico
│   ├── scripts/             # Scripts SQL de referencia (documentación)
│   ├── docs/                # Documentación adicional
│   ├── macros/              # Macros de dbt
│   └── tests/               # Tests SQL personalizados
├── preguntas_negocio/       # Notebooks de análisis de negocio
├── Dockerfile               # Dockerfile del proyecto
├── docker-compose.yml       # Docker Compose
└── env.example              # Variables de entorno de ejemplo
```

---

## Inicio Rápido

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Configurar variables de entorno (opcional)
cp env.example .env

# 2. Iniciar todos los servicios
docker-compose up -d

# 3. Acceder a servicios
# - PostgreSQL: localhost:5432
# - pgAdmin: http://localhost:8080
# - Jupyter: http://localhost:8888
# - dbt: docker-compose exec dbt bash
```

### Opción 2: Instalación Local

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp env.example .env
# Editar .env con tus credenciales de PostgreSQL
```

---

## Proyecto dbt

### Configuración

El proyecto dbt transforma los datos del e-commerce siguiendo las mejores prácticas de ingeniería de datos.

**Archivo de configuración:** `dbt/dbt_project.yml`

**Variables del Proyecto:**
- `database`: Nombre de la base de datos (default: `avance_1_db`)
- `schema`: Esquema de la base de datos (default: `public`)

**Materialización:**
- **Staging**: `view` (vistas para eficiencia)
- **Intermediate**: `view` (vistas para eficiencia)
- **Marts**: `table` (tablas para rendimiento en consultas)

### Dependencias

Este proyecto requiere:
- dbt-core
- dbt-postgres (adaptador para PostgreSQL)
- dbt-utils (para tests adicionales)

---

## Capas de Transformación

### 1. Staging (stg_*)

Modelos que limpian y estandarizan los datos fuente. Cada modelo:
- Lee desde las tablas fuente (`source`)
- Aplica limpieza básica (trim, upper, lower, regexp_replace)
- Valida datos (filtros, checks)
- Agrega campos calculados simples y flags de calidad

**Técnicas aplicadas:**
- Limpieza de texto: `TRIM`, `UPPER`, `LOWER`, `REGEXP_REPLACE`
- Normalización de formatos: DNI, email, códigos postales
- Normalización numérica: redondeo, validación de rangos
- Normalización de fechas: manejo de valores nulos, validación de fechas futuras
- Manejo de valores nulos: `COALESCE`, valores por defecto
- Flags de calidad: `email_valido`, `dni_valido`, `precio_cero`, etc.

**Modelos:**
- `stg_usuarios` - Limpieza de datos de usuarios
- `stg_categorias` - Normalización de categorías
- `stg_productos` - Limpieza y validación de productos
- `stg_ordenes` - Normalización de órdenes
- `stg_detalle_ordenes` - Validación de detalles
- `stg_direcciones_envio` - Normalización de direcciones
- `stg_carrito` - Limpieza de carrito
- `stg_metodos_pago` - Normalización de métodos de pago
- `stg_ordenes_metodos_pago` - Validación de pagos
- `stg_resenas_productos` - Limpieza de reseñas
- `stg_historial_pagos` - Normalización de historial

### 2. Intermediate (int_*)

Modelos que combinan múltiples tablas de staging y realizan transformaciones más complejas:
- Agregaciones
- Joins entre tablas
- Cálculos de métricas
- Preparación para marts

**Modelos:**
- `int_ordenes_detalle` - Combina órdenes con detalles y productos
- `int_ordenes_agregadas` - Métricas agregadas por orden
- `int_productos_resenas` - Productos con métricas de reseñas
- `int_usuarios_ordenes` - Usuarios con métricas de órdenes
- `int_ordenes_pagos` - Órdenes con información de pagos
- `int_ventas_diarias` - Agregación de ventas por día
- `int_ventas_mensuales` - Agregación de ventas por mes

### 3. Marts (fct_* y dim_*)

Modelos finales siguiendo el modelo dimensional de Kimball.

#### Tablas de Hechos (fct_*)
- `fct_ventas` - Hechos de ventas con métricas de negocio
- `fct_pagos` - Hechos de pagos y transacciones
- `fct_resenas` - Hechos de reseñas y calificaciones

#### Tablas de Dimensiones (dim_*)
- `dim_usuarios` - Dimensión de usuarios con segmentación
- `dim_productos` - Dimensión de productos con métricas
- `dim_categorias` - Dimensión de categorías (SCD Type 1)
- `dim_metodos_pago` - Dimensión de métodos de pago (SCD Type 1)
- `dim_fecha` - Dimensión de fecha (tabla de fechas estática)

---

## Modelo Dimensional

El proyecto implementa un modelo dimensional completo siguiendo la metodología Kimball:

### Esquema Estrella

```
                    dim_fecha
                        │
        ┌───────────────┼───────────────┐
        │               │               │
    dim_usuarios    dim_productos   dim_categorias
        │               │               │
        │               └───────┬───────┘
        │                       │
        └───────────┬───────────┘
                    │
            ┌───────┼───────┐
            │       │       │
        fct_ventas  │   fct_resenas
                    │
                fct_pagos
```

### Relaciones

**fct_ventas:**
- `usuario_id` → `dim_usuarios.usuario_id`
- `producto_id` → `dim_productos.producto_id`
- `categoria_id` → `dim_categorias.categoria_id` (nullable)
- `fecha_venta_id` → `dim_fecha.fecha_id`

**fct_pagos:**
- `usuario_id` → `dim_usuarios.usuario_id`
- `metodo_pago_id` → `dim_metodos_pago.metodo_pago_id`
- `fecha_pago_id` → `dim_fecha.fecha_id`

**fct_resenas:**
- `usuario_id` → `dim_usuarios.usuario_id`
- `producto_id` → `dim_productos.producto_id`
- `fecha_resena_id` → `dim_fecha.fecha_id`

**dim_productos:**
- `categoria_id` → `dim_categorias.categoria_id` (nullable)

---

## Slowly Changing Dimensions (SCD)

El proyecto implementa diferentes tipos de SCD según las necesidades de cada dimensión.

### SCD Type 1 (Sin Historial)

**Dimensiones:**
- `dim_categorias` - Las categorías raramente cambian
- `dim_metodos_pago` - Los métodos de pago son estables
- `dim_fecha` - Dimensión estática (pre-poblada)

**Características:**
- Los cambios sobrescriben los valores anteriores
- No se mantiene historial
- Útil para datos que no requieren análisis histórico

### SCD Type 2 (Con Historial Completo)

**Dimensiones:**
- `dim_productos_scd2` - Historial de precios, stock y categorías
- `dim_usuarios_scd2` - Historial de segmentación y métricas

**Características:**
- Mantiene todas las versiones históricas
- Cada cambio crea un nuevo registro
- Campos SCD:
  - `fecha_inicio_validez`: Fecha desde la cual la versión es válida
  - `fecha_fin_validez`: Fecha hasta la cual la versión es válida (9999-12-31 para actual)
  - `es_actual`: Indicador booleano de versión actual
  - `scd_id`: ID único del registro SCD

**Snapshots configurados:**
- `snap_productos` - Rastrea cambios en: `precio`, `stock`, `estado_stock`, `categoria_id`
- `snap_usuarios` - Rastrea cambios en: `segmento_cliente`, `total_ordenes`, `total_gastado`, `email`

**Estrategia:** `check` (detecta cambios en columnas específicas)

**Modelos SCD:**
- `dim_productos_scd2` - Versión histórica de productos
- `dim_usuarios_scd2` - Versión histórica de usuarios
- `dim_productos_scd1` - Versión actual de productos (sin historial)
- `dim_usuarios_scd1` - Versión actual de usuarios (sin historial)

**Uso en Consultas:**

```sql
-- Obtener versión actual de un producto
SELECT * FROM dim_productos_scd2 
WHERE producto_id = 123 AND es_actual = true;

-- Obtener precio histórico de un producto en una fecha específica
SELECT * FROM dim_productos_scd2 
WHERE producto_id = 123 
  AND '2024-01-15'::date BETWEEN fecha_inicio_validez::date 
                              AND fecha_fin_validez::date;
```

---

## Modelo Físico (DDL)

El proyecto incluye scripts SQL DDL para crear el modelo físico del data warehouse directamente en PostgreSQL.

**Ubicación:** `dbt/sql/`

**Scripts disponibles:**
- `00_create_all_tables.sql` - Script principal (ejecuta todos)
- `01_create_dimension_tables.sql` - Crea tablas de dimensiones
- `02_create_fact_tables.sql` - Crea tablas de hechos
- `03_create_indexes.sql` - Crea índices para optimización
- `04_create_foreign_keys.sql` - Crea foreign keys (opcional, comentadas por defecto)
- `05_populate_dim_fecha.sql` - Pobla tabla de fechas

**Orden de Ejecución:**
1. `01_create_dimension_tables.sql` - Crea todas las tablas de dimensiones
2. `02_create_fact_tables.sql` - Crea todas las tablas de hechos
3. `03_create_indexes.sql` - Crea índices para optimización
4. `04_create_foreign_keys.sql` - Crea foreign keys (opcional)
5. `05_populate_dim_fecha.sql` - Pobla la tabla de dimensiones de fecha

**Tablas Creadas:**

**Dimensiones:**
- `dim_fecha` - Dimensión de tiempo (estática)
- `dim_categorias` - Dimensión de categorías (SCD Type 1)
- `dim_metodos_pago` - Dimensión de métodos de pago (SCD Type 1)
- `dim_productos` - Dimensión de productos (base)
- `dim_usuarios` - Dimensión de usuarios (base)
- `dim_productos_scd2` - Dimensión de productos con historial (SCD Type 2)
- `dim_usuarios_scd2` - Dimensión de usuarios con historial (SCD Type 2)

**Hechos:**
- `fct_ventas` - Hechos de ventas (tabla principal)
- `fct_pagos` - Hechos de pagos
- `fct_resenas` - Hechos de reseñas

**Esquemas:**
- Las tablas se crean en el esquema `marts`
- `marts.dim_*` - Tablas de dimensiones
- `marts.fct_*` - Tablas de hechos

**Índices:**
- Foreign keys (para joins eficientes)
- Campos de fecha (para filtros temporales)
- Campos de búsqueda frecuente (segmento_cliente, estado_stock, etc.)
- Índices compuestos para consultas comunes

**Foreign Keys:**
- Están **comentadas por defecto** para mejor performance en carga masiva
- Para habilitar, descomentar las líneas en `04_create_foreign_keys.sql`

**Población de dim_fecha:**
- Se puebla automáticamente con el rango 2020-2030
- Para cambiar el rango, modificar la llamada a `populate_dim_fecha()` en `05_populate_dim_fecha.sql`

---

## Scripts SQL de Referencia

El proyecto incluye scripts SQL de referencia que documentan las técnicas de transformación utilizadas.

**Ubicación:** `dbt/scripts/`

**Propósito:**
Estos scripts **NO se ejecutan directamente**. Son scripts de referencia y documentación que muestran:
1. Técnicas de transformación utilizadas en los modelos dbt
2. Ejemplos de código SQL para cada tipo de transformación
3. Mejores prácticas y patrones comunes
4. Consultas de ejemplo para casos de uso comunes

**Scripts disponibles:**
- `01_limpieza_normalizacion.sql` - Técnicas de limpieza y normalización
- `02_creacion_hechos_dimensiones.sql` - Creación de hechos y dimensiones
- `03_implementacion_scd.sql` - Implementación de SCD Type 1 y Type 2

**Relación con Modelos dbt:**
Estos scripts documentan las transformaciones que se implementan en:
- **Staging**: `models/staging/stg_*.sql`
- **Intermediate**: `models/intermediate/int_*.sql`
- **Marts**: `models/marts/fact/` y `models/marts/dimension/`
- **Snapshots**: `snapshots/snap_*.sql`

---

## Integridad Referencial

El proyecto incluye tests de relaciones para garantizar integridad referencial entre hechos y dimensiones.

**Archivos:**
- `models/marts/schema.yml` - Tests de relationships a nivel de columna
- `models/marts/relationships.yml` - Tests de integridad referencial a nivel de modelo
- `macros/validate_relationship.sql` - Macro para validar relaciones personalizadas
- `docs/RELACIONES.md` - Documentación completa de relaciones

**Tests de Integridad Referencial:**

Los tests de `relationships` se definen en los archivos `schema.yml`:

```yaml
- name: usuario_id
  description: "ID del usuario (Foreign key a dim_usuarios)"
  tests:
    - relationships:
        to: ref('dim_usuarios')
        field: usuario_id
```

**Manejo de Valores Nulos:**
Algunas relaciones permiten valores NULL:
- `fct_ventas.categoria_id` puede ser NULL
- `dim_productos.categoria_id` puede ser NULL

Los tests incluyen cláusulas `where` para manejar estos casos:

```yaml
tests:
  - relationships:
      to: ref('dim_categorias')
      field: categoria_id
      config:
        where: "categoria_id IS NOT NULL"
```

**Orden de Ejecución:**
dbt garantiza el orden correcto mediante:
1. **Dependencias implícitas**: `ref()` y `source()` crean dependencias automáticas
2. **Tests de relaciones**: Se ejecutan después de que los modelos están listos
3. **Validación**: Los tests fallan si hay valores huérfanos

---

## Vistas Analíticas y Storytelling

El proyecto incluye vistas analíticas optimizadas y documentación de storytelling para facilitar el análisis y presentación de insights.

### Vistas Analíticas (`models/analytics/`)

Vistas pre-agregadas optimizadas para análisis rápidos:

- `vw_ventas_resumen` - Resumen de ventas con todas las dimensiones
- `vw_clientes_activos` - Análisis de comportamiento de clientes
- `vw_productos_performance` - Performance de productos
- `vw_ventas_temporales` - Análisis temporal con tendencias
- `vw_pagos_resumen` - Resumen de pagos y transacciones

**Características:**
- Vistas pre-agregadas para queries rápidas
- Optimizadas con índices y agregaciones
- Incluyen métricas calculadas y segmentaciones

### Documentación de Storytelling

**Archivos:**
- `docs/QUERIES_ANALISTAS.md` - Guía completa de queries para analistas (19 queries de ejemplo)
- `docs/STORYTELLING_INSIGHTS.md` - Insights en formato de storytelling con narrativa ejecutiva

**Formato Storytelling:**
- Presenta insights en formato narrativo
- Incluye situación, insight y acción recomendada
- Proporciona queries SQL para explorar cada insight
- Organizado por categorías de negocio (ventas, pagos, clientes, productos)

**Ejemplo de Query para Analistas:**

```sql
-- Productos más vendidos por volumen
SELECT 
    producto_nombre,
    categoria_nombre,
    total_unidades_vendidas,
    total_ventas,
    total_ordenes
FROM marts.vw_productos_performance
ORDER BY total_unidades_vendidas DESC
LIMIT 10;
```

---

## Docker Setup

El proyecto está completamente containerizado usando Docker y Docker Compose.

### Servicios Disponibles

**PostgreSQL (db)**
- Imagen: postgres:16-alpine
- Puerto: 5432 (configurable)
- Volúmenes persistentes para datos
- Healthcheck configurado

**pgAdmin (pgadmin)**
- Interfaz web para gestionar PostgreSQL
- Puerto: 8080 (configurable)
- Acceso: http://localhost:8080
- Email: `admin@ecommerce.com` (configurable)
- Password: `admin` (configurable)

**dbt (dbt)**
- Contenedor con dbt y todas las herramientas
- Variables de entorno configuradas
- Volúmenes montados para el proyecto
- Listo para ejecutar comandos dbt

**Jupyter (jupyter)**
- Servidor Jupyter Lab
- Puerto: 8888 (configurable)
- Acceso: http://localhost:8888
- Sin token (configurado para desarrollo)

### Configuración

**Variables de Entorno:**
Crear archivo `.env` basado en `env.example`:

```bash
cp env.example .env
```

Editar `.env` para personalizar:
- Credenciales de PostgreSQL
- Puertos de servicios
- Configuraciones de pgAdmin y Jupyter

**Perfiles de dbt:**
Los perfiles de dbt están en `dbt_profiles/profiles.yml`. Se montan automáticamente en el contenedor.

### Volúmenes

Los datos se persisten en volúmenes Docker:
- `postgres_data`: Datos de PostgreSQL
- `pgadmin_data`: Configuración de pgAdmin
- `jupyter_data`: Configuración de Jupyter

---

## Uso y Comandos

### Comandos dbt

```bash
# Compilar modelos
dbt compile

# Ejecutar modelos
dbt run

# Ejecutar solo staging
dbt run --select staging

# Ejecutar solo intermedios
dbt run --select intermediate

# Ejecutar solo marts
dbt run --select marts

# Ejecutar tests
dbt test

# Ejecutar snapshots (SCD Type 2)
dbt snapshot

# Generar documentación
dbt docs generate
dbt docs serve
```

### Comandos Docker

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Ver logs
docker-compose logs -f

# Ejecutar dbt desde Docker
docker-compose exec dbt dbt run

# Ejecutar tests desde Docker
docker-compose exec dbt dbt test

# Ejecutar snapshots desde Docker
docker-compose exec dbt dbt snapshot

# Conectarse a PostgreSQL
docker-compose exec db psql -U usuario -d avance_1_db
```

### Ejecutar Scripts DDL

```bash
# Opción 1: Desde Docker
docker-compose exec db psql -U usuario -d avance_1_db -f /app/dbt/sql/00_create_all_tables.sql

# Opción 2: Localmente
psql -U usuario -d database -f dbt/sql/00_create_all_tables.sql

# Opción 3: Desde psql interactivo
\i dbt/sql/01_create_dimension_tables.sql
\i dbt/sql/02_create_fact_tables.sql
\i dbt/sql/03_create_indexes.sql
\i dbt/sql/04_create_foreign_keys.sql
\i dbt/sql/05_populate_dim_fecha.sql
```

### Flujo de Trabajo Recomendado

1. **Inicialización:**
   ```bash
   # Iniciar servicios
   docker-compose up -d
   
   # Crear estructura de base de datos
   docker-compose exec db psql -U usuario -d avance_1_db -f /app/dbt/sql/00_create_all_tables.sql
   ```

2. **Desarrollo con dbt:**
   ```bash
   # Entrar al contenedor dbt
   docker-compose exec dbt bash
   
   # Navegar al directorio dbt
   cd /app/dbt
   
   # Ejecutar modelos
   dbt run
   
   # Ejecutar tests
   dbt test
   
   # Ejecutar snapshots
   dbt snapshot
   ```

3. **Análisis:**
   - Acceder a Jupyter: http://localhost:8888
   - Acceder a pgAdmin: http://localhost:8080
   - Consultar vistas analíticas desde cualquier cliente SQL

---

## Notas Importantes

- Los modelos de staging asumen que las tablas fuente están en el esquema `public` por defecto
- Las tablas de hechos y dimensiones siguen el modelo dimensional de Kimball
- Se incluyen tests de calidad de datos en los modelos de staging
- Los modelos están documentados con descripciones y tests en los archivos `schema.yml`
- Los SCD Type 2 mantienen historial completo de cambios para análisis temporales
- Los scripts DDL crean el modelo físico directamente en PostgreSQL
- Los tests de relationships garantizan integridad referencial entre hechos y dimensiones
- Las vistas analíticas están optimizadas para queries rápidas por parte de analistas
- El formato storytelling facilita la presentación de insights a stakeholders

---

## Tecnologías Utilizadas

- **Python 3.10+**
- **PostgreSQL 16**
- **dbt** (Data Build Tool)
- **SQLAlchemy** (ORM)
- **Jupyter** (Notebooks)
- **Docker** (Containerización)
- **Docker Compose** (Orquestación)

---

## Referencias

- [dbt Documentation](https://docs.getdbt.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Kimball Methodology](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

