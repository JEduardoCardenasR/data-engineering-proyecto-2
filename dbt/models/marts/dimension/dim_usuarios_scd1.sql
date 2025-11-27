{{
    config(
        materialized='table'
    )
}}

-- Dimensión de Usuarios SCD Type 1
-- Versión actualizada sin historial (sobrescribe valores anteriores)
-- Útil para consultas que solo necesitan el estado actual
select
    usuario_id,
    nombre,
    apellido,
    nombre_completo,
    email,
    fecha_registro,
    total_ordenes,
    total_gastado,
    promedio_por_orden,
    primera_orden,
    ultima_orden,
    ordenes_completadas,
    ordenes_pendientes,
    segmento_cliente,
    anio_registro,
    mes_registro,
    -- Indicador de última actualización
    current_timestamp as fecha_ultima_actualizacion
from {{ ref('dim_usuarios') }}
where usuario_id is not null

