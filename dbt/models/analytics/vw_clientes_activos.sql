{{
    config(
        materialized='view',
        description='Vista analítica: Clientes activos con métricas de comportamiento'
    )
}}

-- Vista analítica: Clientes Activos
-- Optimizada para análisis de comportamiento de clientes
SELECT
    du.usuario_id,
    du.nombre_completo,
    du.email,
    du.segmento_cliente,
    du.fecha_registro,
    du.anio_registro,
    du.mes_registro,
    
    -- Métricas de actividad
    du.total_ordenes,
    du.total_gastado,
    du.promedio_por_orden,
    du.ordenes_completadas,
    du.ordenes_pendientes,
    
    -- Fechas importantes
    du.primera_orden,
    du.ultima_orden,
    
    -- Cálculo de días desde última compra
    CASE 
        WHEN du.ultima_orden IS NOT NULL 
        THEN CURRENT_DATE - du.ultima_orden::date
        ELSE NULL
    END as dias_desde_ultima_compra,
    
    -- Cálculo de días como cliente
    CURRENT_DATE - du.fecha_registro::date as dias_como_cliente,
    
    -- Indicadores
    CASE 
        WHEN du.ultima_orden IS NOT NULL 
             AND (CURRENT_DATE - du.ultima_orden::date) <= 30 
        THEN 'Activo'
        WHEN du.ultima_orden IS NOT NULL 
             AND (CURRENT_DATE - du.ultima_orden::date) <= 90 
        THEN 'Inactivo Reciente'
        WHEN du.ultima_orden IS NOT NULL 
        THEN 'Inactivo'
        ELSE 'Nunca Compró'
    END as estado_cliente,
    
    -- Métricas de reseñas
    COUNT(DISTINCT fr.resena_id) as total_resenas,
    AVG(fr.calificacion) as calificacion_promedio_dada
    
FROM {{ ref('dim_usuarios') }} du
LEFT JOIN {{ ref('fct_resenas') }} fr
    ON du.usuario_id = fr.usuario_id
GROUP BY
    du.usuario_id, du.nombre_completo, du.email, du.segmento_cliente,
    du.fecha_registro, du.anio_registro, du.mes_registro,
    du.total_ordenes, du.total_gastado, du.promedio_por_orden,
    du.ordenes_completadas, du.ordenes_pendientes,
    du.primera_orden, du.ultima_orden

