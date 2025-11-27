{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'usuarios') }}
),

renamed as (
    select
        usuario_id,
        -- Limpieza de nombres: trim, upper, eliminar espacios múltiples
        regexp_replace(trim(upper(nombre)), '\s+', ' ', 'g') as nombre,
        regexp_replace(trim(upper(apellido)), '\s+', ' ', 'g') as apellido,
        -- Limpieza de DNI: eliminar espacios y caracteres especiales, solo números
        regexp_replace(trim(dni), '[^0-9]', '', 'g') as dni,
        -- Limpieza de email: lower, trim, validar formato básico
        lower(trim(email)) as email,
        -- Normalización de fecha
        case 
            when fecha_registro is null then current_timestamp
            else fecha_registro
        end as fecha_registro
    from source
),

final as (
    select
        usuario_id,
        nombre,
        apellido,
        dni,
        email,
        fecha_registro,
        -- Validaciones mejoradas
        case 
            when email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' then true
            else false
        end as email_valido,
        case 
            when length(regexp_replace(trim(dni), '[^0-9]', '', 'g')) >= 8 then true
            else false
        end as dni_valido,
        -- Flags de calidad de datos
        case 
            when nombre is null or trim(nombre) = '' then true
            else false
        end as nombre_incompleto,
        case 
            when apellido is null or trim(apellido) = '' then true
            else false
        end as apellido_incompleto
    from renamed
    -- Filtrar registros con datos mínimos requeridos
    where nombre is not null 
      and apellido is not null
      and dni is not null
      and email is not null
)

select * from final

