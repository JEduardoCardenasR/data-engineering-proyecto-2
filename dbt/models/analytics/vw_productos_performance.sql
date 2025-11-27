{{
    config(
        materialized='view',
        description='Vista analítica: Performance de productos con métricas de ventas y reseñas'
    )
}}

-- Vista analítica: Performance de Productos
-- Optimizada para análisis de productos
SELECT
    dp.producto_id,
    dp.nombre as producto_nombre,
    dp.categoria_nombre,
    dp.precio,
    dp.stock,
    dp.estado_stock,
    
    -- Métricas de ventas
    COUNT(DISTINCT fv.orden_id) as total_ordenes,
    SUM(fv.cantidad) as total_unidades_vendidas,
    SUM(fv.subtotal) as total_revenue,
    AVG(fv.precio_unitario) as precio_promedio_vendido,
    MIN(fv.precio_unitario) as precio_minimo_vendido,
    MAX(fv.precio_unitario) as precio_maximo_vendido,
    
    -- Métricas de reseñas
    dp.total_resenas,
    dp.calificacion_promedio,
    dp.resenas_positivas,
    dp.resenas_negativas,
    dp.porcentaje_resenas_positivas,
    dp.categoria_calificacion,
    
    -- Análisis de rotación
    CASE 
        WHEN dp.stock > 0 
        THEN SUM(fv.cantidad)::float / dp.stock
        ELSE NULL
    END as ratio_rotacion,
    
    -- Indicadores de performance
    CASE 
        WHEN SUM(fv.subtotal) > 10000 AND dp.calificacion_promedio >= 4.0 
        THEN 'Estrella'
        WHEN SUM(fv.subtotal) > 5000 
        THEN 'Alto Valor'
        WHEN dp.calificacion_promedio >= 4.5 
        THEN 'Alta Calificación'
        WHEN dp.stock = 0 
        THEN 'Agotado'
        WHEN dp.stock > 100 AND SUM(fv.cantidad) < 10 
        THEN 'Baja Rotación'
        ELSE 'Regular'
    END as categoria_performance,
    
    -- Última venta
    MAX(fv.fecha_venta_id) as ultima_venta
    
FROM {{ ref('dim_productos') }} dp
LEFT JOIN {{ ref('fct_ventas') }} fv
    ON dp.producto_id = fv.producto_id
GROUP BY
    dp.producto_id, dp.nombre, dp.categoria_nombre, dp.precio,
    dp.stock, dp.estado_stock, dp.total_resenas, dp.calificacion_promedio,
    dp.resenas_positivas, dp.resenas_negativas, dp.porcentaje_resenas_positivas,
    dp.categoria_calificacion

