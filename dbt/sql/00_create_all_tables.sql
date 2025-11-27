-- ============================================================================
-- Script DDL Principal: Crear Todo el Modelo Físico del Data Warehouse
-- Modelo Dimensional - Kimball Methodology
-- Base de datos: PostgreSQL
-- ============================================================================
-- 
-- Este script ejecuta todos los scripts DDL en el orden correcto:
-- 1. Crear tablas de dimensiones
-- 2. Crear tablas de hechos
-- 3. Crear índices
-- 4. Crear foreign keys (opcional)
-- 5. Poblar dim_fecha
--
-- Uso: psql -U usuario -d database -f 00_create_all_tables.sql
-- ============================================================================

\echo 'Iniciando creación del modelo físico del data warehouse...'

-- Ejecutar scripts en orden
\echo '1. Creando tablas de dimensiones...'
\i 01_create_dimension_tables.sql

\echo '2. Creando tablas de hechos...'
\i 02_create_fact_tables.sql

\echo '3. Creando índices...'
\i 03_create_indexes.sql

\echo '4. Creando foreign keys (opcional, comentadas por defecto)...'
\i 04_create_foreign_keys.sql

\echo '5. Poblando tabla de fechas...'
\i 05_populate_dim_fecha.sql

\echo 'Modelo físico creado exitosamente!'

-- Verificar tablas creadas
\echo 'Verificando tablas creadas...'
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'marts'
ORDER BY tablename;

