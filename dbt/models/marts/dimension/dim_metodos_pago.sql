{{
    config(
        materialized='table'
    )
}}

-- Tabla de dimensiones: Métodos de Pago
-- Modelo dimensional siguiendo el esquema estrella de Kimball
with metodos_pago as (
    select * from {{ ref('stg_metodos_pago') }}
),

ordenes_metodos_pago as (
    select * from {{ ref('stg_ordenes_metodos_pago') }}
),

metodos_pago_agregados as (
    select
        mp.metodo_pago_id,
        mp.nombre,
        mp.descripcion,
        -- Métricas agregadas
        count(omp.orden_metodo_id) as total_usos,
        sum(omp.monto_pagado) as total_monto_pagado,
        avg(omp.monto_pagado) as promedio_monto_pagado,
        min(omp.monto_pagado) as monto_minimo,
        max(omp.monto_pagado) as monto_maximo
    from metodos_pago mp
    left join ordenes_metodos_pago omp
        on mp.metodo_pago_id = omp.metodo_pago_id
    group by
        mp.metodo_pago_id,
        mp.nombre,
        mp.descripcion
)

select * from metodos_pago_agregados

