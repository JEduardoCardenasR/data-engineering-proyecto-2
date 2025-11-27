{{
    config(
        materialized='table'
    )
}}

-- Dimensión de Productos SCD Type 1
-- Versión actualizada sin historial (sobrescribe valores anteriores)
-- Útil para consultas que solo necesitan el estado actual
select
    producto_id,
    nombre,
    descripcion,
    precio,
    stock,
    categoria_id,
    estado_stock,
    categoria_nombre,
    categoria_descripcion,
    total_resenas,
    calificacion_promedio,
    categoria_calificacion,
    porcentaje_resenas_positivas,
    -- Indicador de última actualización
    current_timestamp as fecha_ultima_actualizacion
from {{ ref('dim_productos') }}
where producto_id is not null

