{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'metodos_pago') }}
),

renamed as (
    select
        metodo_pago_id,
        -- Limpieza de nombre: trim, upper, eliminar espacios múltiples
        regexp_replace(trim(upper(nombre)), '\s+', ' ', 'g') as nombre,
        -- Limpieza de descripción: trim, eliminar espacios múltiples
        case 
            when descripcion is null or trim(descripcion) = '' then null
            else regexp_replace(trim(descripcion), '\s+', ' ', 'g')
        end as descripcion
    from source
),

final as (
    select
        metodo_pago_id,
        nombre,
        coalesce(descripcion, 'Sin descripción') as descripcion,
        -- Validaciones de calidad
        case 
            when nombre is null or trim(nombre) = '' then true
            else false
        end as nombre_incompleto
    from renamed
    where nombre is not null
      and trim(nombre) != ''
)

select * from final

