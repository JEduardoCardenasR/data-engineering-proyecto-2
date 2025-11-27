{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'historial_pagos') }}
),

renamed as (
    select
        pago_id,
        orden_id,
        metodo_pago_id,
        -- Normalización de monto: redondear a 2 decimales, validar positivo
        case 
            when monto < 0 then 0
            else round(cast(monto as numeric), 2)
        end as monto,
        -- Normalización de fecha: usar fecha actual si es nula
        case 
            when fecha_pago is null then current_timestamp
            else fecha_pago
        end as fecha_pago,
        -- Normalización de estado: valores estándar
        case 
            when trim(upper(estado_pago)) in ('COMPLETADO', 'COMPLETA', 'COMPLETO', 'APROBADO') then 'COMPLETADO'
            when trim(upper(estado_pago)) in ('PENDIENTE', 'PROCESANDO', 'EN PROCESO') then 'PROCESANDO'
            when trim(upper(estado_pago)) in ('RECHAZADO', 'RECHAZADA', 'FALLIDO', 'ERROR') then 'RECHAZADO'
            when trim(upper(estado_pago)) in ('CANCELADO', 'CANCELADA', 'CANCEL') then 'CANCELADO'
            when estado_pago is null or trim(estado_pago) = '' then 'PROCESANDO'
            else trim(upper(estado_pago))
        end as estado_pago
    from source
),

final as (
    select
        pago_id,
        orden_id,
        metodo_pago_id,
        monto,
        fecha_pago,
        estado_pago,
        -- Campos calculados
        extract(year from fecha_pago) as anio_pago,
        extract(month from fecha_pago) as mes_pago,
        extract(day from fecha_pago) as dia_pago,
        date_trunc('month', fecha_pago) as mes_completo_pago,
        -- Validaciones de calidad
        case 
            when monto = 0 then true
            else false
        end as monto_cero,
        case 
            when fecha_pago > current_timestamp then true
            else false
        end as fecha_futura
    from renamed
    where orden_id is not null
      and metodo_pago_id is not null
      and monto > 0
)

select * from final

