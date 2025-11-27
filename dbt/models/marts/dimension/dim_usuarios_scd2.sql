{{
    config(
        materialized='table'
    )
}}

-- Dimensión de Usuarios con SCD Type 2
-- Esta tabla incluye el historial completo de cambios en usuarios (especialmente segmentación)
with usuarios_snapshot as (
    select * from {{ ref('snap_usuarios') }}
),

-- Agregar campos de SCD Type 2 al snapshot
usuarios_scd2 as (
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
        -- Campos SCD Type 2
        dbt_valid_from as fecha_inicio_validez,
        coalesce(dbt_valid_to, '9999-12-31'::timestamp) as fecha_fin_validez,
        case 
            when dbt_valid_to is null then true
            else false
        end as es_actual,
        dbt_scd_id as scd_id
    from usuarios_snapshot
)

select * from usuarios_scd2
order by usuario_id, fecha_inicio_validez desc

