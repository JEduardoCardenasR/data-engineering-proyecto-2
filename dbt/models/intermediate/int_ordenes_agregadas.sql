{{
    config(
        materialized='view'
    )
}}

-- Modelo intermedio que agrega métricas por orden
with ordenes_detalle as (
    select * from {{ ref('int_ordenes_detalle') }}
),

ordenes_agregadas as (
    select
        orden_id,
        usuario_id,
        fecha_orden,
        total_orden,
        estado_orden,
        anio_orden,
        mes_orden,
        mes_completo,
        -- Métricas agregadas
        count(distinct producto_id) as cantidad_productos_diferentes,
        sum(cantidad) as cantidad_total_items,
        sum(subtotal) as subtotal_calculado,
        avg(precio_unitario) as precio_promedio_unitario,
        min(precio_unitario) as precio_minimo,
        max(precio_unitario) as precio_maximo
    from ordenes_detalle
    group by
        orden_id,
        usuario_id,
        fecha_orden,
        total_orden,
        estado_orden,
        anio_orden,
        mes_orden,
        mes_completo
)

select * from ordenes_agregadas

