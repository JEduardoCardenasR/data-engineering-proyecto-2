{{
    config(
        materialized='view',
        description='Vista analítica: Resumen de pagos y transacciones'
    )
}}

-- Vista analítica: Resumen de Pagos
-- Optimizada para análisis de pagos y transacciones
SELECT
    -- Dimensión de tiempo
    df.fecha_id,
    df.anio,
    df.mes,
    df.trimestre,
    df.nombre_mes,
    
    -- Dimensión de método de pago
    dmp.metodo_pago_id,
    dmp.nombre as metodo_pago_nombre,
    
    -- Dimensión de usuarios
    du.usuario_id,
    du.segmento_cliente,
    
    -- Métricas de pagos
    COUNT(DISTINCT fp.pago_id) as total_pagos,
    COUNT(DISTINCT fp.orden_id) as total_ordenes_pagadas,
    SUM(fp.monto_pago) as total_recaudado,
    AVG(fp.monto_pago) as monto_promedio_pago,
    MIN(fp.monto_pago) as monto_minimo,
    MAX(fp.monto_pago) as monto_maximo,
    
    -- Análisis de estados
    SUM(CASE WHEN fp.pago_completado = TRUE THEN 1 ELSE 0 END) as pagos_completados,
    SUM(CASE WHEN fp.estado_pago = 'PROCESANDO' THEN 1 ELSE 0 END) as pagos_procesando,
    SUM(CASE WHEN fp.estado_pago = 'RECHAZADO' THEN 1 ELSE 0 END) as pagos_rechazados,
    
    -- Tasa de éxito
    CASE 
        WHEN COUNT(DISTINCT fp.pago_id) > 0
        THEN (SUM(CASE WHEN fp.pago_completado = TRUE THEN 1 ELSE 0 END)::float 
              / COUNT(DISTINCT fp.pago_id)) * 100
        ELSE 0
    END as tasa_exito_pct
    
FROM {{ ref('fct_pagos') }} fp
LEFT JOIN {{ ref('dim_fecha') }} df
    ON fp.fecha_pago_id = df.fecha_id
LEFT JOIN {{ ref('dim_metodos_pago') }} dmp
    ON fp.metodo_pago_id = dmp.metodo_pago_id
LEFT JOIN {{ ref('dim_usuarios') }} du
    ON fp.usuario_id = du.usuario_id
GROUP BY
    df.fecha_id, df.anio, df.mes, df.trimestre, df.nombre_mes,
    dmp.metodo_pago_id, dmp.nombre,
    du.usuario_id, du.segmento_cliente

