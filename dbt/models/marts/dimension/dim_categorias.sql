{{
    config(
        materialized='table'
    )
}}

-- Tabla de dimensiones: Categorías
-- Modelo dimensional siguiendo el esquema estrella de Kimball
with categorias as (
    select * from {{ ref('stg_categorias') }}
),

productos as (
    select * from {{ ref('stg_productos') }}
),

categorias_agregadas as (
    select
        c.categoria_id,
        c.nombre,
        c.descripcion,
        -- Métricas agregadas
        count(p.producto_id) as total_productos,
        sum(p.stock) as stock_total,
        avg(p.precio) as precio_promedio,
        min(p.precio) as precio_minimo,
        max(p.precio) as precio_maximo,
        sum(case when p.stock = 0 then 1 else 0 end) as productos_agotados
    from categorias c
    left join productos p
        on c.categoria_id = p.categoria_id
    group by
        c.categoria_id,
        c.nombre,
        c.descripcion
)

select * from categorias_agregadas

