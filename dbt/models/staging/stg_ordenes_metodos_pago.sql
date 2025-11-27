{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'ordenes_metodos_pago') }}
),

renamed as (
    select
        orden_metodo_id,
        orden_id,
        metodo_pago_id,
        -- Normalización de monto: redondear a 2 decimales, validar positivo
        case 
            when monto_pagado < 0 then 0
            else round(cast(monto_pagado as numeric), 2)
        end as monto_pagado
    from source
),

final as (
    select
        orden_metodo_id,
        orden_id,
        metodo_pago_id,
        monto_pagado,
        -- Validaciones de calidad
        case 
            when monto_pagado = 0 then true
            else false
        end as monto_cero
    from renamed
    where orden_id is not null
      and metodo_pago_id is not null
      and monto_pagado > 0
)

select * from final

