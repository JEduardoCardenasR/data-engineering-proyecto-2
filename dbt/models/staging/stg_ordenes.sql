{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'ordenes') }}
),

renamed as (
    select
        orden_id,
        usuario_id,
        -- Normalización de fecha: usar fecha actual si es nula
        case 
            when fecha_orden is null then current_timestamp
            else fecha_orden
        end as fecha_orden,
        -- Normalización de total: redondear a 2 decimales, validar positivo
        case 
            when total < 0 then 0
            else round(cast(total as numeric), 2)
        end as total,
        -- Normalización de estado: trim, upper, valores estándar
        case 
            when trim(upper(estado)) in ('COMPLETADA', 'COMPLETADO', 'COMPLETA') then 'COMPLETADA'
            when trim(upper(estado)) in ('PENDIENTE', 'PENDIENTE') then 'PENDIENTE'
            when trim(upper(estado)) in ('CANCELADA', 'CANCELADO', 'CANCEL') then 'CANCELADA'
            when trim(upper(estado)) in ('EN PROCESO', 'PROCESO', 'PROCESANDO') then 'EN_PROCESO'
            when estado is null or trim(estado) = '' then 'PENDIENTE'
            else trim(upper(estado))
        end as estado
    from source
),

final as (
    select
        orden_id,
        usuario_id,
        fecha_orden,
        total,
        estado,
        -- Campos calculados
        extract(year from fecha_orden) as anio_orden,
        extract(month from fecha_orden) as mes_orden,
        extract(day from fecha_orden) as dia_orden,
        date_trunc('month', fecha_orden) as mes_completo,
        -- Validaciones de calidad
        case 
            when total = 0 then true
            else false
        end as total_cero,
        case 
            when fecha_orden > current_timestamp then true
            else false
        end as fecha_futura
    from renamed
    where usuario_id is not null
)

select * from final

