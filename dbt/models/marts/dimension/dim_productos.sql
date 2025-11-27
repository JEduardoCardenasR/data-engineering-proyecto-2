{{
    config(
        materialized='table'
    )
}}

-- Tabla de dimensiones: Productos
-- Modelo dimensional siguiendo el esquema estrella de Kimball
with productos_resenas as (
    select * from {{ ref('int_productos_resenas') }}
),

categorias as (
    select * from {{ ref('stg_categorias') }}
),

final as (
    select
        -- Clave primaria
        p.producto_id,
        
        -- Atributos descriptivos
        p.nombre_producto as nombre,
        p.precio,
        p.stock,
        p.estado_stock,
        p.categoria_id,
        c.nombre as categoria_nombre,
        c.descripcion as categoria_descripcion,
        
        -- Métricas de reseñas
        coalesce(p.total_resenas, 0) as total_resenas,
        coalesce(p.calificacion_promedio, 0) as calificacion_promedio,
        p.calificacion_minima,
        p.calificacion_maxima,
        coalesce(p.resenas_positivas, 0) as resenas_positivas,
        coalesce(p.resenas_negativas, 0) as resenas_negativas,
        coalesce(p.resenas_neutras, 0) as resenas_neutras,
        
        -- Campos calculados
        case 
            when p.calificacion_promedio >= 4.5 then 'Excelente'
            when p.calificacion_promedio >= 4.0 then 'Muy bueno'
            when p.calificacion_promedio >= 3.0 then 'Bueno'
            when p.calificacion_promedio >= 2.0 then 'Regular'
            else 'Malo'
        end as categoria_calificacion,
        
        case 
            when p.total_resenas = 0 then 0
            else (p.resenas_positivas::float / p.total_resenas) * 100
        end as porcentaje_resenas_positivas
    from productos_resenas p
    left join categorias c
        on p.categoria_id = c.categoria_id
)

select * from final

