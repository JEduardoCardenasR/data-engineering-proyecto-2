{{
    config(
        materialized='table'
    )
}}

-- Tabla de hechos: Ventas
-- Modelo dimensional siguiendo el esquema estrella de Kimball
with ordenes_detalle as (
    select * from {{ ref('int_ordenes_detalle') }}
),

final as (
    select
        -- Claves foráneas a dimensiones
        detalle_id as venta_id,
        orden_id,
        usuario_id,
        producto_id,
        categoria_id,
        fecha_orden::date as fecha_venta_id,
        
        -- Medidas (métricas)
        cantidad,
        precio_unitario,
        subtotal,
        
        -- Atributos descriptivos
        nombre_producto,
        estado_stock,
        estado_orden,
        
        -- Campos de fecha para particionamiento
        anio_orden,
        mes_orden,
        mes_completo
    from ordenes_detalle
)

select * from final

