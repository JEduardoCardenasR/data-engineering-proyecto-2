{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'resenas_productos') }}
),

renamed as (
    select
        resena_id,
        usuario_id,
        producto_id,
        -- Normalización de calificación: validar rango 1-5
        case 
            when calificacion < 1 then 1
            when calificacion > 5 then 5
            else cast(calificacion as integer)
        end as calificacion,
        -- Limpieza de comentario: trim, eliminar espacios múltiples
        case 
            when comentario is null or trim(comentario) = '' then null
            else regexp_replace(trim(comentario), '\s+', ' ', 'g')
        end as comentario,
        -- Normalización de fecha: usar fecha actual si es nula
        case 
            when fecha is null then current_timestamp
            else fecha
        end as fecha
    from source
),

final as (
    select
        resena_id,
        usuario_id,
        producto_id,
        calificacion,
        coalesce(comentario, 'Sin comentario') as comentario,
        fecha,
        -- Campos calculados
        case 
            when calificacion >= 4 then 'Positiva'
            when calificacion = 3 then 'Neutra'
            else 'Negativa'
        end as sentimiento_resena,
        extract(year from fecha) as anio_resena,
        extract(month from fecha) as mes_resena,
        -- Validaciones de calidad
        case 
            when comentario is null or trim(comentario) = '' then true
            else false
        end as sin_comentario,
        case 
            when fecha > current_timestamp then true
            else false
        end as fecha_futura
    from renamed
    where usuario_id is not null
      and producto_id is not null
      and calificacion between 1 and 5
)

select * from final

