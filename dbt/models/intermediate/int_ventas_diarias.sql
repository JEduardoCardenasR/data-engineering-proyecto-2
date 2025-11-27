{{
    config(
        materialized='view'
    )
}}

-- Modelo intermedio que agrega ventas por día
with ordenes_detalle as (
    select * from {{ ref('int_ordenes_detalle') }}
),

ventas_diarias as (
    select
        date_trunc('day', fecha_orden) as fecha,
        extract(year from fecha_orden) as anio,
        extract(month from fecha_orden) as mes,
        extract(day from fecha_orden) as dia,
        -- Métricas agregadas
        count(distinct orden_id) as total_ordenes,
        count(distinct usuario_id) as total_usuarios,
        count(distinct producto_id) as total_productos_vendidos,
        sum(cantidad) as total_items_vendidos,
        sum(subtotal) as total_ventas,
        avg(subtotal) as promedio_venta_por_item,
        min(subtotal) as venta_minima,
        max(subtotal) as venta_maxima
    from ordenes_detalle
    group by
        date_trunc('day', fecha_orden),
        extract(year from fecha_orden),
        extract(month from fecha_orden),
        extract(day from fecha_orden)
)

select * from ventas_diarias
order by fecha desc

