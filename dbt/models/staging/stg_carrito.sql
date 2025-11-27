{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'carrito') }}
),

renamed as (
    select
        carrito_id,
        usuario_id,
        producto_id,
        -- Normalización de cantidad: validar positivo, convertir a entero
        case 
            when cantidad < 0 then 0
            else cast(cantidad as integer)
        end as cantidad,
        -- Normalización de fecha: usar fecha actual si es nula
        case 
            when fecha_agregado is null then current_timestamp
            else fecha_agregado
        end as fecha_agregado
    from source
),

final as (
    select
        carrito_id,
        usuario_id,
        producto_id,
        cantidad,
        fecha_agregado,
        -- Campos calculados
        extract(year from fecha_agregado) as anio_agregado,
        extract(month from fecha_agregado) as mes_agregado,
        date_trunc('day', fecha_agregado) as dia_agregado,
        -- Validaciones de calidad
        case 
            when cantidad = 0 then true
            else false
        end as cantidad_cero,
        case 
            when fecha_agregado > current_timestamp then true
            else false
        end as fecha_futura
    from renamed
    where usuario_id is not null
      and producto_id is not null
      and cantidad > 0
)

select * from final

