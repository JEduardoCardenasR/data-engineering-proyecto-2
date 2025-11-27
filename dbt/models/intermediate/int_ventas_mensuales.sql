{{
    config(
        materialized='view'
    )
}}

-- Modelo intermedio que agrega ventas por mes
with ordenes_detalle as (
    select * from {{ ref('int_ordenes_detalle') }}
),

ventas_mensuales as (
    select
        mes_completo as fecha,
        anio_orden as anio,
        mes_orden as mes,
        -- Métricas agregadas
        count(distinct orden_id) as total_ordenes,
        count(distinct usuario_id) as total_usuarios,
        count(distinct producto_id) as total_productos_vendidos,
        sum(cantidad) as total_items_vendidos,
        sum(subtotal) as total_ventas,
        avg(subtotal) as promedio_venta_por_item,
        min(subtotal) as venta_minima,
        max(subtotal) as venta_maxima,
        -- Comparación con mes anterior (usando window function)
        lag(sum(subtotal)) over (order by mes_completo) as ventas_mes_anterior
    from ordenes_detalle
    group by
        mes_completo,
        anio_orden,
        mes_orden
)

select 
    *,
    case 
        when ventas_mes_anterior is not null 
        then total_ventas - ventas_mes_anterior
        else null
    end as diferencia_mes_anterior,
    case 
        when ventas_mes_anterior is not null and ventas_mes_anterior > 0
        then ((total_ventas - ventas_mes_anterior) / ventas_mes_anterior) * 100
        else null
    end as porcentaje_cambio_mes_anterior
from ventas_mensuales
order by fecha desc

