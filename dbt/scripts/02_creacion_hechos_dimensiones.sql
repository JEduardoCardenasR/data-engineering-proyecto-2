-- ============================================================================
-- Script SQL de Referencia: Creación de Tablas de Hechos y Dimensiones
-- Este script muestra cómo se construyen las tablas del modelo dimensional
-- ============================================================================
-- 
-- Este archivo documenta el proceso de creación de hechos y dimensiones.
-- Las transformaciones reales están en: models/marts/fact/ y models/marts/dimension/
-- 
-- NOTA: Para la implementación física (DDL), ver: sql/01_create_dimension_tables.sql
--       y sql/02_create_fact_tables.sql
-- ============================================================================

-- ============================================================================
-- 1. CREACIÓN DE TABLAS DE HECHOS
-- ============================================================================

-- ============================================================================
-- 1.1 Tabla de Hechos: Ventas (fct_ventas)
-- ============================================================================

-- Estructura básica de una tabla de hechos
WITH ordenes_detalle AS (
    -- Combinar datos de múltiples tablas fuente
    SELECT
        o.orden_id,
        o.usuario_id,
        o.fecha_orden,
        o.total as total_orden,
        o.estado as estado_orden,
        d.detalle_id,
        d.producto_id,
        d.cantidad,
        d.precio_unitario,
        d.cantidad * d.precio_unitario as subtotal,
        p.categoria_id,
        p.nombre as nombre_producto,
        p.estado_stock
    FROM staging.stg_ordenes o
    INNER JOIN staging.stg_detalle_ordenes d
        ON o.orden_id = d.orden_id
    LEFT JOIN staging.stg_productos p
        ON d.producto_id = p.producto_id
),
final AS (
    SELECT
        -- Claves foráneas a dimensiones
        detalle_id as venta_id,  -- Surrogate key
        orden_id,                 -- Natural key
        usuario_id,              -- FK a dim_usuarios
        producto_id,             -- FK a dim_productos
        categoria_id,            -- FK a dim_categorias
        fecha_orden::date as fecha_venta_id,  -- FK a dim_fecha
        
        -- Medidas (métricas numéricas)
        cantidad,
        precio_unitario,
        subtotal,
        
        -- Atributos descriptivos (denormalizados para performance)
        nombre_producto,
        estado_stock,
        estado_orden,
        
        -- Campos de fecha para particionamiento
        EXTRACT(YEAR FROM fecha_orden) as anio_orden,
        EXTRACT(MONTH FROM fecha_orden) as mes_orden,
        DATE_TRUNC('month', fecha_orden)::date as mes_completo
    FROM ordenes_detalle
)
SELECT * FROM final;

-- ============================================================================
-- 1.2 Tabla de Hechos: Pagos (fct_pagos)
-- ============================================================================

WITH ordenes_pagos AS (
    SELECT
        o.orden_id,
        o.usuario_id,
        hp.pago_id,
        hp.metodo_pago_id,
        hp.monto,
        hp.fecha_pago,
        hp.estado_pago,
        mp.nombre as metodo_pago_nombre,
        o.total as total_orden
    FROM staging.stg_ordenes o
    INNER JOIN staging.stg_historial_pagos hp
        ON o.orden_id = hp.orden_id
    LEFT JOIN staging.stg_metodos_pago mp
        ON hp.metodo_pago_id = mp.metodo_pago_id
    WHERE hp.pago_id IS NOT NULL
)
SELECT
    -- Claves foráneas
    pago_id,
    orden_id,
    usuario_id,
    metodo_pago_id,
    fecha_pago::date as fecha_pago_id,
    
    -- Medidas
    monto as monto_pago,
    monto_pagado,
    total_orden,
    
    -- Atributos
    metodo_pago_nombre,
    estado_pago,
    estado_orden,
    CASE 
        WHEN estado_pago = 'COMPLETADO' THEN TRUE
        ELSE FALSE
    END as pago_completado,
    
    -- Campos de fecha
    EXTRACT(YEAR FROM fecha_pago) as anio_pago,
    EXTRACT(MONTH FROM fecha_pago) as mes_pago,
    DATE_TRUNC('month', fecha_pago)::date as mes_completo_pago
FROM ordenes_pagos;

-- ============================================================================
-- 1.3 Tabla de Hechos: Reseñas (fct_resenas)
-- ============================================================================

SELECT
    -- Claves foráneas
    resena_id,
    usuario_id,
    producto_id,
    fecha::date as fecha_resena_id,
    
    -- Medidas
    calificacion,
    
    -- Atributos
    comentario,
    sentimiento_resena,
    
    -- Campos de fecha
    EXTRACT(YEAR FROM fecha) as anio_resena,
    EXTRACT(MONTH FROM fecha) as mes_resena,
    DATE_TRUNC('month', fecha)::date as mes_completo_resena
FROM staging.stg_resenas_productos;

-- ============================================================================
-- 2. CREACIÓN DE TABLAS DE DIMENSIONES
-- ============================================================================

-- ============================================================================
-- 2.1 Dimensión: Usuarios (dim_usuarios)
-- ============================================================================

WITH usuarios_ordenes AS (
    -- Agregar métricas de órdenes por usuario
    SELECT
        u.usuario_id,
        u.nombre,
        u.apellido,
        u.email,
        u.fecha_registro,
        COUNT(o.orden_id) as total_ordenes,
        SUM(o.total) as total_gastado,
        AVG(o.total) as promedio_por_orden,
        MIN(o.fecha_orden) as primera_orden,
        MAX(o.fecha_orden) as ultima_orden,
        SUM(CASE WHEN o.estado = 'COMPLETADA' THEN 1 ELSE 0 END) as ordenes_completadas,
        SUM(CASE WHEN o.estado = 'PENDIENTE' THEN 1 ELSE 0 END) as ordenes_pendientes
    FROM staging.stg_usuarios u
    LEFT JOIN staging.stg_ordenes o
        ON u.usuario_id = o.usuario_id
    GROUP BY
        u.usuario_id,
        u.nombre,
        u.apellido,
        u.email,
        u.fecha_registro
)
SELECT
    -- Clave primaria
    usuario_id,
    
    -- Atributos descriptivos
    nombre,
    apellido,
    CONCAT(nombre, ' ', apellido) as nombre_completo,
    email,
    fecha_registro,
    
    -- Métricas agregadas
    total_ordenes,
    total_gastado,
    promedio_por_orden,
    primera_orden,
    ultima_orden,
    ordenes_completadas,
    ordenes_pendientes,
    
    -- Campos calculados
    CASE 
        WHEN total_ordenes = 0 THEN 'Nuevo'
        WHEN total_ordenes BETWEEN 1 AND 5 THEN 'Ocasional'
        WHEN total_ordenes BETWEEN 6 AND 20 THEN 'Regular'
        ELSE 'VIP'
    END as segmento_cliente,
    
    -- Campos de fecha
    EXTRACT(YEAR FROM fecha_registro) as anio_registro,
    EXTRACT(MONTH FROM fecha_registro) as mes_registro
FROM usuarios_ordenes;

-- ============================================================================
-- 2.2 Dimensión: Productos (dim_productos)
-- ============================================================================

WITH productos_resenas AS (
    -- Agregar métricas de reseñas por producto
    SELECT
        p.producto_id,
        p.nombre as nombre_producto,
        p.precio,
        p.stock,
        p.estado_stock,
        p.categoria_id,
        COUNT(r.resena_id) as total_resenas,
        AVG(r.calificacion) as calificacion_promedio,
        MIN(r.calificacion) as calificacion_minima,
        MAX(r.calificacion) as calificacion_maxima,
        SUM(CASE WHEN r.sentimiento_resena = 'Positiva' THEN 1 ELSE 0 END) as resenas_positivas,
        SUM(CASE WHEN r.sentimiento_resena = 'Negativa' THEN 1 ELSE 0 END) as resenas_negativas,
        SUM(CASE WHEN r.sentimiento_resena = 'Neutra' THEN 1 ELSE 0 END) as resenas_neutras
    FROM staging.stg_productos p
    LEFT JOIN staging.stg_resenas_productos r
        ON p.producto_id = r.producto_id
    GROUP BY
        p.producto_id,
        p.nombre,
        p.precio,
        p.stock,
        p.estado_stock,
        p.categoria_id
)
SELECT
    p.producto_id,
    p.nombre_producto as nombre,
    p.precio,
    p.stock,
    p.estado_stock,
    p.categoria_id,
    c.nombre as categoria_nombre,
    c.descripcion as categoria_descripcion,
    
    -- Métricas de reseñas
    COALESCE(p.total_resenas, 0) as total_resenas,
    COALESCE(p.calificacion_promedio, 0) as calificacion_promedio,
    p.calificacion_minima,
    p.calificacion_maxima,
    COALESCE(p.resenas_positivas, 0) as resenas_positivas,
    COALESCE(p.resenas_negativas, 0) as resenas_negativas,
    COALESCE(p.resenas_neutras, 0) as resenas_neutras,
    
    -- Campos calculados
    CASE 
        WHEN p.calificacion_promedio >= 4.5 THEN 'Excelente'
        WHEN p.calificacion_promedio >= 4.0 THEN 'Muy bueno'
        WHEN p.calificacion_promedio >= 3.0 THEN 'Bueno'
        WHEN p.calificacion_promedio >= 2.0 THEN 'Regular'
        ELSE 'Malo'
    END as categoria_calificacion,
    
    CASE 
        WHEN p.total_resenas = 0 THEN 0
        ELSE (p.resenas_positivas::FLOAT / p.total_resenas) * 100
    END as porcentaje_resenas_positivas
FROM productos_resenas p
LEFT JOIN staging.stg_categorias c
    ON p.categoria_id = c.categoria_id;

-- ============================================================================
-- 2.3 Dimensión: Fecha (dim_fecha)
-- ============================================================================

-- NOTA: La implementación completa y ejecutable de dim_fecha está en:
-- sql/05_populate_dim_fecha.sql
-- 
-- Este script crea una función populate_dim_fecha() que genera y pobla
-- la tabla dim_fecha con todos los campos necesarios para análisis temporal.

-- Ejemplo simplificado de la estructura de dim_fecha:
-- La tabla incluye campos como:
--   - fecha_id (DATE, PK)
--   - anio, mes, dia, trimestre, semana
--   - nombre_mes, nombre_dia_semana
--   - es_fin_semana (BOOLEAN)
--   - estacion (VARCHAR)
--   - Y otros campos temporales para análisis

-- Para poblar dim_fecha, usar la función:
-- SELECT populate_dim_fecha('2020-01-01'::date, '2030-12-31'::date);

-- La lógica completa de generación está en sql/05_populate_dim_fecha.sql

-- ============================================================================
-- 3. PRINCIPIOS DEL MODELO DIMENSIONAL
-- ============================================================================

-- 3.1 Tablas de Hechos:
--     - Contienen medidas (métricas numéricas)
--     - Tienen claves foráneas a dimensiones
--     - Granularidad: nivel de detalle de cada fila
--     - Pueden tener atributos descriptivos denormalizados

-- 3.2 Tablas de Dimensiones:
--     - Contienen atributos descriptivos
--     - Tienen una clave primaria (surrogate key)
--     - Pueden tener métricas agregadas (SCD Type 1)
--     - Proporcionan contexto para los hechos

-- 3.3 Esquema Estrella:
--     - Una tabla de hechos central
--     - Múltiples tablas de dimensiones alrededor
--     - Relaciones uno-a-muchos entre hechos y dimensiones

