{{
    config(
        materialized='view'
    )
}}

-- Modelo intermedio que combina productos con sus reseñas
with productos as (
    select * from {{ ref('stg_productos') }}
),

resenas as (
    select * from {{ ref('stg_resenas_productos') }}
),

productos_resenas as (
    select
        p.producto_id,
        p.nombre as nombre_producto,
        p.precio,
        p.stock,
        p.categoria_id,
        p.estado_stock,
        -- Métricas de reseñas
        count(r.resena_id) as total_resenas,
        avg(r.calificacion) as calificacion_promedio,
        min(r.calificacion) as calificacion_minima,
        max(r.calificacion) as calificacion_maxima,
        sum(case when r.sentimiento_resena = 'Positiva' then 1 else 0 end) as resenas_positivas,
        sum(case when r.sentimiento_resena = 'Negativa' then 1 else 0 end) as resenas_negativas,
        sum(case when r.sentimiento_resena = 'Neutra' then 1 else 0 end) as resenas_neutras
    from productos p
    left join resenas r
        on p.producto_id = r.producto_id
    group by
        p.producto_id,
        p.nombre,
        p.precio,
        p.stock,
        p.categoria_id,
        p.estado_stock
)

select * from productos_resenas

