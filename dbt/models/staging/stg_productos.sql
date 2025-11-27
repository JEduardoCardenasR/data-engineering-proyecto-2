{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'productos') }}
),

renamed as (
    select
        producto_id,
        -- Limpieza de nombre: trim, eliminar espacios múltiples
        regexp_replace(trim(nombre), '\s+', ' ', 'g') as nombre,
        -- Limpieza de descripción: trim, eliminar espacios múltiples, manejar nulos
        case 
            when descripcion is null or trim(descripcion) = '' then null
            else regexp_replace(trim(descripcion), '\s+', ' ', 'g')
        end as descripcion,
        -- Normalización de precio: redondear a 2 decimales, validar positivo
        case 
            when precio < 0 then 0
            else round(cast(precio as numeric), 2)
        end as precio,
        -- Normalización de stock: validar no negativo
        case 
            when stock < 0 then 0
            else stock
        end as stock,
        categoria_id
    from source
),

final as (
    select
        producto_id,
        nombre,
        coalesce(descripcion, 'Sin descripción') as descripcion,
        precio,
        stock,
        categoria_id,
        -- Campos calculados
        case 
            when stock = 0 then 'Agotado'
            when stock < 10 then 'Bajo stock'
            else 'Disponible'
        end as estado_stock,
        -- Validaciones de calidad
        case 
            when nombre is null or trim(nombre) = '' then true
            else false
        end as nombre_incompleto,
        case 
            when precio = 0 then true
            else false
        end as precio_cero
    from renamed
    where nombre is not null
      and trim(nombre) != ''
)

select * from final

