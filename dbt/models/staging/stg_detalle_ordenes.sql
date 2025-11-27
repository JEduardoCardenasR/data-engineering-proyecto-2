{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'detalle_ordenes') }}
),

renamed as (
    select
        detalle_id,
        orden_id,
        producto_id,
        -- Normalización de cantidad: validar positivo, convertir a entero
        case 
            when cantidad < 0 then 0
            else cast(cantidad as integer)
        end as cantidad,
        -- Normalización de precio: redondear a 2 decimales, validar positivo
        case 
            when precio_unitario < 0 then 0
            else round(cast(precio_unitario as numeric), 2)
        end as precio_unitario
    from source
),

final as (
    select
        detalle_id,
        orden_id,
        producto_id,
        cantidad,
        precio_unitario,
        -- Campos calculados
        round(cast(cantidad * precio_unitario as numeric), 2) as subtotal,
        -- Validaciones de calidad
        case 
            when cantidad = 0 then true
            else false
        end as cantidad_cero,
        case 
            when precio_unitario = 0 then true
            else false
        end as precio_cero
    from renamed
    where orden_id is not null
      and producto_id is not null
      and cantidad > 0
      and precio_unitario > 0
)

select * from final

