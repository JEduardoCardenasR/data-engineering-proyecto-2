-- ============================================================================
-- Script SQL de Referencia: Implementación de Slowly Changing Dimensions
-- Este script muestra cómo se implementan SCD Type 1 y Type 2 con dbt
-- ============================================================================
-- 
-- Este archivo documenta el proceso de implementación de SCD.
-- Las implementaciones reales están en: snapshots/ y models/marts/dimension/
-- ============================================================================

-- ============================================================================
-- 1. SCD TYPE 1: Sin Historial (Actualización Directa)
-- ============================================================================

-- SCD Type 1 sobrescribe los valores anteriores cuando hay cambios.
-- No se mantiene historial.

-- Ejemplo: dim_categorias (SCD Type 1)
-- Cuando cambia una categoría, se actualiza directamente:

UPDATE marts.dim_categorias
SET 
    nombre = 'Nuevo Nombre',
    descripcion = 'Nueva Descripción',
    fecha_ultima_actualizacion = CURRENT_TIMESTAMP
WHERE categoria_id = 123;

-- O usando dbt (modelo materializado como table):
-- models/marts/dimension/dim_categorias.sql
SELECT
    categoria_id,
    nombre,
    descripcion,
    -- Métricas agregadas (se actualizan)
    total_productos,
    stock_total,
    precio_promedio,
    CURRENT_TIMESTAMP as fecha_ultima_actualizacion
FROM staging.stg_categorias;

-- ============================================================================
-- 2. SCD TYPE 2: Con Historial Completo (Snapshots de dbt)
-- ============================================================================

-- SCD Type 2 mantiene todas las versiones históricas.
-- Cada cambio crea un nuevo registro.

-- ============================================================================
-- 2.1 Configuración de Snapshot en dbt
-- ============================================================================

-- Archivo: snapshots/snap_productos.sql
/*
{% snapshot snap_productos %}

{{
    config(
      target_schema='snapshots',
      unique_key='producto_id',
      strategy='check',
      check_cols=['precio', 'stock', 'estado_stock', 'categoria_id'],
      invalidate_hard_deletes=True,
    )
}}

SELECT
    producto_id,
    nombre,
    precio,
    stock,
    estado_stock,
    categoria_id
FROM {{ ref('dim_productos') }}

{% endsnapshot %}
*/

-- ============================================================================
-- 2.2 Estrategias de Snapshot
-- ============================================================================

-- Estrategia 'check': Detecta cambios en columnas específicas
-- Útil cuando se quiere rastrear cambios en campos específicos

-- Estrategia 'timestamp': Usa un campo de timestamp para detectar cambios
-- Útil cuando hay un campo de última actualización

-- Ejemplo con estrategia 'timestamp':
/*
{{
    config(
      unique_key='usuario_id',
      strategy='timestamp',
      updated_at='fecha_ultima_actualizacion',
    )
}}
*/

-- ============================================================================
-- 2.3 Modelo SCD Type 2 desde Snapshot
-- ============================================================================

-- Archivo: models/marts/dimension/dim_productos_scd2.sql
-- Este modelo lee del snapshot y agrega campos SCD

WITH productos_snapshot AS (
    SELECT * FROM {{ ref('snap_productos') }}
)
SELECT
    producto_id,
    nombre,
    precio,
    stock,
    estado_stock,
    categoria_id,
    
    -- Campos SCD Type 2 (generados automáticamente por dbt)
    dbt_valid_from as fecha_inicio_validez,
    COALESCE(dbt_valid_to, '9999-12-31'::timestamp) as fecha_fin_validez,
    CASE 
        WHEN dbt_valid_to IS NULL THEN TRUE
        ELSE FALSE
    END as es_actual,
    dbt_scd_id as scd_id
FROM productos_snapshot
ORDER BY producto_id, fecha_inicio_validez DESC;

-- ============================================================================
-- 3. CAMPOS GENERADOS POR DBT EN SNAPSHOTS
-- ============================================================================

-- dbt_valid_from: Fecha/hora desde la cual esta versión es válida
-- dbt_valid_to: Fecha/hora hasta la cual esta versión es válida (NULL para actual)
-- dbt_scd_id: ID único del registro SCD (hash de los valores)

-- ============================================================================
-- 4. CONSULTAS CON SCD TYPE 2
-- ============================================================================

-- ============================================================================
-- 4.1 Obtener Versión Actual
-- ============================================================================

SELECT *
FROM marts.dim_productos_scd2
WHERE producto_id = 123
  AND es_actual = TRUE;

-- ============================================================================
-- 4.2 Obtener Versión en Fecha Específica
-- ============================================================================

SELECT *
FROM marts.dim_productos_scd2
WHERE producto_id = 123
  AND '2024-06-15'::date >= fecha_inicio_validez::date
  AND '2024-06-15'::date < fecha_fin_validez::date;

-- ============================================================================
-- 4.3 Ver Historial Completo de Cambios
-- ============================================================================

SELECT 
    producto_id,
    nombre,
    precio,
    stock,
    fecha_inicio_validez,
    fecha_fin_validez,
    es_actual
FROM marts.dim_productos_scd2
WHERE producto_id = 123
ORDER BY fecha_inicio_validez DESC;

-- ============================================================================
-- 4.4 Comparar Versiones (Precio Actual vs Histórico)
-- ============================================================================

WITH version_actual AS (
    SELECT precio as precio_actual
    FROM marts.dim_productos_scd2
    WHERE producto_id = 123 AND es_actual = TRUE
),
version_historica AS (
    SELECT precio as precio_historico
    FROM marts.dim_productos_scd2
    WHERE producto_id = 123
      AND '2024-01-01'::date >= fecha_inicio_validez::date
      AND '2024-01-01'::date < fecha_fin_validez::date
)
SELECT 
    precio_actual,
    precio_historico,
    precio_actual - precio_historico as diferencia,
    ((precio_actual - precio_historico) / precio_historico) * 100 as porcentaje_cambio
FROM version_actual, version_historica;

-- ============================================================================
-- 5. EJECUTAR SNAPSHOTS EN DBT
-- ============================================================================

-- Comando para ejecutar todos los snapshots:
-- dbt snapshot

-- Comando para ejecutar un snapshot específico:
-- dbt snapshot --select snap_productos

-- Los snapshots se ejecutan periódicamente (diariamente recomendado)
-- para capturar cambios en las dimensiones.

-- ============================================================================
-- 6. MEJORES PRÁCTICAS PARA SCD
-- ============================================================================

-- 6.1 Selección de Campos para 'check_cols':
--     - Incluir solo campos que realmente cambian y son importantes
--     - No incluir campos calculados o timestamps
--     - Considerar el impacto en performance

-- 6.2 Estrategia de Snapshot:
--     - 'check': Para cambios en campos específicos
--     - 'timestamp': Cuando hay campo de última actualización confiable

-- 6.3 Mantenimiento:
--     - Ejecutar snapshots regularmente (diariamente)
--     - Monitorear crecimiento de tablas SCD Type 2
--     - Considerar archivado de datos históricos antiguos

-- 6.4 Performance:
--     - Crear índices en producto_id/usuario_id y fechas
--     - Usar particionamiento por fecha si es necesario
--     - Considerar compresión para datos históricos

-- ============================================================================
-- 7. EJEMPLO COMPLETO: SCD Type 2 para Usuarios
-- ============================================================================

-- Snapshot: snapshots/snap_usuarios.sql
/*
{% snapshot snap_usuarios %}
{{
    config(
      target_schema='snapshots',
      unique_key='usuario_id',
      strategy='check',
      check_cols=['segmento_cliente', 'total_ordenes', 'total_gastado', 'email'],
    )
}}
SELECT
    usuario_id,
    nombre,
    apellido,
    email,
    segmento_cliente,
    total_ordenes,
    total_gastado
FROM {{ ref('dim_usuarios') }}
{% endsnapshot %}
*/

-- Modelo SCD Type 2: models/marts/dimension/dim_usuarios_scd2.sql
/*
WITH usuarios_snapshot AS (
    SELECT * FROM {{ ref('snap_usuarios') }}
)
SELECT
    usuario_id,
    nombre,
    apellido,
    email,
    segmento_cliente,
    total_ordenes,
    total_gastado,
    dbt_valid_from as fecha_inicio_validez,
    COALESCE(dbt_valid_to, '9999-12-31'::timestamp) as fecha_fin_validez,
    CASE 
        WHEN dbt_valid_to IS NULL THEN TRUE
        ELSE FALSE
    END as es_actual,
    dbt_scd_id as scd_id
FROM usuarios_snapshot
ORDER BY usuario_id, fecha_inicio_validez DESC;
*/

-- Consulta: Ver evolución de segmentación de un usuario
/*
SELECT 
    usuario_id,
    segmento_cliente,
    total_ordenes,
    fecha_inicio_validez,
    fecha_fin_validez,
    es_actual
FROM marts.dim_usuarios_scd2
WHERE usuario_id = 456
ORDER BY fecha_inicio_validez DESC;
*/

