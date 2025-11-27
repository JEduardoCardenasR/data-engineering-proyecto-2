{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'direcciones_envio') }}
),

renamed as (
    select
        direccion_id,
        usuario_id,
        -- Limpieza de calle: trim, eliminar espacios múltiples
        regexp_replace(trim(calle), '\s+', ' ', 'g') as calle,
        -- Limpieza de ciudad: trim, upper, eliminar espacios múltiples
        regexp_replace(trim(upper(ciudad)), '\s+', ' ', 'g') as ciudad,
        -- Limpieza de campos opcionales
        case 
            when departamento is null or trim(departamento) = '' then null
            else regexp_replace(trim(upper(departamento)), '\s+', ' ', 'g')
        end as departamento,
        case 
            when provincia is null or trim(provincia) = '' then null
            else regexp_replace(trim(upper(provincia)), '\s+', ' ', 'g')
        end as provincia,
        case 
            when distrito is null or trim(distrito) = '' then null
            else regexp_replace(trim(upper(distrito)), '\s+', ' ', 'g')
        end as distrito,
        case 
            when estado is null or trim(estado) = '' then null
            else regexp_replace(trim(upper(estado)), '\s+', ' ', 'g')
        end as estado,
        -- Limpieza de código postal: solo números y letras
        case 
            when codigo_postal is null or trim(codigo_postal) = '' then null
            else upper(regexp_replace(trim(codigo_postal), '[^A-Z0-9]', '', 'g'))
        end as codigo_postal,
        -- Limpieza de país: trim, upper
        trim(upper(pais)) as pais
    from source
),

final as (
    select
        direccion_id,
        usuario_id,
        calle,
        ciudad,
        coalesce(departamento, 'N/A') as departamento,
        coalesce(provincia, 'N/A') as provincia,
        coalesce(distrito, 'N/A') as distrito,
        coalesce(estado, 'N/A') as estado,
        codigo_postal,
        pais,
        -- Dirección completa
        concat(
            calle, ', ',
            ciudad, ', ',
            coalesce(provincia, ''), ', ',
            pais
        ) as direccion_completa,
        -- Validaciones de calidad
        case 
            when calle is null or trim(calle) = '' then true
            else false
        end as calle_incompleta,
        case 
            when ciudad is null or trim(ciudad) = '' then true
            else false
        end as ciudad_incompleta,
        case 
            when codigo_postal is null or length(codigo_postal) < 4 then true
            else false
        end as codigo_postal_invalido
    from renamed
    where usuario_id is not null
      and calle is not null
      and trim(calle) != ''
      and ciudad is not null
      and trim(ciudad) != ''
      and pais is not null
      and trim(pais) != ''
)

select * from final

