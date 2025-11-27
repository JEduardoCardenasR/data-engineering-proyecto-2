{{
    config(
        materialized='view'
    )
}}

-- Modelo intermedio que combina órdenes con sus detalles
with ordenes as (
    select * from {{ ref('stg_ordenes') }}
),

detalle_ordenes as (
    select * from {{ ref('stg_detalle_ordenes') }}
),

productos as (
    select * from {{ ref('stg_productos') }}
),

ordenes_con_detalle as (
    select
        o.orden_id,
        o.usuario_id,
        o.fecha_orden,
        o.total as total_orden,
        o.estado as estado_orden,
        o.anio_orden,
        o.mes_orden,
        o.mes_completo,
        d.detalle_id,
        d.producto_id,
        d.cantidad,
        d.precio_unitario,
        d.subtotal,
        p.nombre as nombre_producto,
        p.precio as precio_actual_producto,
        p.categoria_id,
        p.estado_stock
    from ordenes o
    inner join detalle_ordenes d
        on o.orden_id = d.orden_id
    left join productos p
        on d.producto_id = p.producto_id
)

select * from ordenes_con_detalle

