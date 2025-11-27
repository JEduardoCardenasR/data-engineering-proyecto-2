{{
    config(
        materialized='view'
    )
}}

-- Modelo intermedio que combina órdenes con información de pagos
with ordenes as (
    select * from {{ ref('stg_ordenes') }}
),

ordenes_metodos_pago as (
    select * from {{ ref('stg_ordenes_metodos_pago') }}
),

metodos_pago as (
    select * from {{ ref('stg_metodos_pago') }}
),

historial_pagos as (
    select * from {{ ref('stg_historial_pagos') }}
),

ordenes_pagos as (
    select
        o.orden_id,
        o.usuario_id,
        o.fecha_orden,
        o.total as total_orden,
        o.estado as estado_orden,
        -- Información de métodos de pago
        omp.metodo_pago_id,
        mp.nombre as metodo_pago_nombre,
        omp.monto_pagado,
        -- Información de historial de pagos
        hp.pago_id,
        hp.monto as monto_historial,
        hp.fecha_pago,
        hp.estado_pago,
        -- Campos calculados
        case 
            when hp.estado_pago = 'COMPLETADO' then true
            else false
        end as pago_completado
    from ordenes o
    left join ordenes_metodos_pago omp
        on o.orden_id = omp.orden_id
    left join metodos_pago mp
        on omp.metodo_pago_id = mp.metodo_pago_id
    left join historial_pagos hp
        on o.orden_id = hp.orden_id
)

select * from ordenes_pagos

