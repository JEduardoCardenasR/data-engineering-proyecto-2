{{
    config(
        materialized='table'
    )
}}

-- Tabla de hechos: Pagos
-- Modelo dimensional siguiendo el esquema estrella de Kimball
with ordenes_pagos as (
    select * from {{ ref('int_ordenes_pagos') }}
),

final as (
    select
        -- Claves foráneas a dimensiones
        pago_id,
        orden_id,
        usuario_id,
        metodo_pago_id,
        fecha_pago::date as fecha_pago_id,
        
        -- Medidas (métricas)
        monto as monto_pago,
        monto_pagado,
        total_orden,
        
        -- Atributos descriptivos
        metodo_pago_nombre,
        estado_pago,
        estado_orden,
        pago_completado,
        
        -- Campos de fecha para particionamiento
        extract(year from fecha_pago) as anio_pago,
        extract(month from fecha_pago) as mes_pago,
        date_trunc('month', fecha_pago) as mes_completo_pago
    from ordenes_pagos
    where pago_id is not null
)

select * from final

