{{
    config(
        materialized='view',
        description='Vista analítica: Análisis temporal de ventas optimizado'
    )
}}

-- Vista analítica: Análisis Temporal de Ventas
-- Optimizada para análisis de tendencias temporales
SELECT
    df.fecha_id,
    df.anio,
    df.trimestre,
    df.mes,
    df.semana,
    df.dia,
    df.dia_semana,
    df.nombre_dia_semana,
    df.nombre_mes,
    df.es_fin_semana,
    df.estacion,
    df.mes_completo,
    df.trimestre_completo,
    
    -- Métricas agregadas por día
    COUNT(DISTINCT fv.orden_id) as total_ordenes,
    COUNT(DISTINCT fv.usuario_id) as total_clientes_unicos,
    COUNT(DISTINCT fv.producto_id) as total_productos_vendidos,
    SUM(fv.cantidad) as total_unidades,
    SUM(fv.subtotal) as total_ventas,
    AVG(fv.subtotal) as ticket_promedio,
    
    -- Comparaciones
    LAG(SUM(fv.subtotal)) OVER (ORDER BY df.fecha_id) as ventas_dia_anterior,
    LAG(SUM(fv.subtotal)) OVER (PARTITION BY df.dia_semana ORDER BY df.fecha_id) as ventas_mismo_dia_semana_anterior,
    
    -- Cálculos de crecimiento
    CASE 
        WHEN LAG(SUM(fv.subtotal)) OVER (ORDER BY df.fecha_id) > 0
        THEN ((SUM(fv.subtotal) - LAG(SUM(fv.subtotal)) OVER (ORDER BY df.fecha_id)) 
              / LAG(SUM(fv.subtotal)) OVER (ORDER BY df.fecha_id)) * 100
        ELSE NULL
    END as crecimiento_dia_anterior_pct,
    
    -- Promedios móviles
    AVG(SUM(fv.subtotal)) OVER (
        ORDER BY df.fecha_id 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as promedio_movil_7_dias,
    
    AVG(SUM(fv.subtotal)) OVER (
        ORDER BY df.fecha_id 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as promedio_movil_30_dias
    
FROM {{ ref('fct_ventas') }} fv
INNER JOIN {{ ref('dim_fecha') }} df
    ON fv.fecha_venta_id = df.fecha_id
GROUP BY
    df.fecha_id, df.anio, df.trimestre, df.mes, df.semana, df.dia,
    df.dia_semana, df.nombre_dia_semana, df.nombre_mes, df.es_fin_semana,
    df.estacion, df.mes_completo, df.trimestre_completo

