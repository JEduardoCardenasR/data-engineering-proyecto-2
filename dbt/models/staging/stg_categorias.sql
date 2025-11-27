{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'categorias') }}
),

renamed as (
    select
        categoria_id,
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
        categoria_id,
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

