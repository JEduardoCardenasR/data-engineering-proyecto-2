{{
    config(
        materialized='view',
        description='Vista analítica: Resumen de ventas optimizado para análisis rápidos'
    )
}}

-- Vista analítica: Resumen de Ventas
-- Optimizada para queries de analistas sobre ventas
SELECT
    -- Dimensión de tiempo
    df.fecha_id,
    df.anio,
    df.mes,
    df.trimestre,
    df.nombre_mes,
    df.dia_semana,
    df.nombre_dia_semana,
    df.es_fin_semana,
    df.estacion,
    
    -- Dimensión de productos
    dp.producto_id,
    dp.nombre as producto_nombre,
    dp.categoria_nombre,
    dp.precio as precio_actual,
    dp.estado_stock,
    dp.calificacion_promedio,
    
    -- Dimensión de usuarios
    du.usuario_id,
    du.nombre_completo as usuario_nombre,
    du.segmento_cliente,
    
    -- Métricas de ventas
    COUNT(DISTINCT fv.orden_id) as total_ordenes,
    SUM(fv.cantidad) as total_unidades_vendidas,
    SUM(fv.subtotal) as total_ventas,
    AVG(fv.subtotal) as ticket_promedio,
    AVG(fv.cantidad) as cantidad_promedio_por_venta,
    MIN(fv.subtotal) as venta_minima,
    MAX(fv.subtotal) as venta_maxima
    
FROM {{ ref('fct_ventas') }} fv
LEFT JOIN {{ ref('dim_fecha') }} df
    ON fv.fecha_venta_id = df.fecha_id
LEFT JOIN {{ ref('dim_productos') }} dp
    ON fv.producto_id = dp.producto_id
LEFT JOIN {{ ref('dim_usuarios') }} du
    ON fv.usuario_id = du.usuario_id
GROUP BY
    df.fecha_id, df.anio, df.mes, df.trimestre, df.nombre_mes,
    df.dia_semana, df.nombre_dia_semana, df.es_fin_semana, df.estacion,
    dp.producto_id, dp.nombre, dp.categoria_nombre, dp.precio,
    dp.estado_stock, dp.calificacion_promedio,
    du.usuario_id, du.nombre_completo, du.segmento_cliente

