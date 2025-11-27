{{
    config(
        materialized='table'
    )
}}

-- Dimensión de Productos con SCD Type 2
-- Esta tabla incluye el historial completo de cambios en productos
with productos_snapshot as (
    select * from {{ ref('snap_productos') }}
),

productos_actuales as (
    select * from {{ ref('dim_productos') }}
),

-- Agregar campos de SCD Type 2 al snapshot
productos_scd2 as (
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
        -- Campos SCD Type 2
        dbt_valid_from as fecha_inicio_validez,
        coalesce(dbt_valid_to, '9999-12-31'::timestamp) as fecha_fin_validez,
        case 
            when dbt_valid_to is null then true
            else false
        end as es_actual,
        dbt_scd_id as scd_id
    from productos_snapshot
)

select * from productos_scd2
order by producto_id, fecha_inicio_validez desc

