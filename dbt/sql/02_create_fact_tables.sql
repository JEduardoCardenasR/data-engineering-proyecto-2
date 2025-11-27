-- ============================================================================
-- Script DDL: Crear Tablas de Hechos del Modelo Dimensional
-- Modelo Físico - Data Warehouse
-- Base de datos: PostgreSQL
-- ============================================================================

-- ============================================================================
-- TABLAS DE HECHOS
-- ============================================================================

-- Tabla: fct_ventas
-- Tabla de hechos principal para análisis de ventas
CREATE TABLE IF NOT EXISTS marts.fct_ventas (
    venta_id INTEGER PRIMARY KEY,
    orden_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    categoria_id INTEGER,
    fecha_venta_id DATE NOT NULL,
    
    -- Medidas (métricas)
    cantidad INTEGER NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL,
    
    -- Atributos descriptivos (denormalizados para performance)
    nombre_producto VARCHAR(255),
    estado_stock VARCHAR(20),
    estado_orden VARCHAR(50),
    
    -- Campos de fecha para particionamiento
    anio_orden INTEGER NOT NULL,
    mes_orden INTEGER NOT NULL,
    mes_completo DATE NOT NULL,
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_cantidad_positiva CHECK (cantidad > 0),
    CONSTRAINT chk_precio_positivo CHECK (precio_unitario >= 0),
    CONSTRAINT chk_subtotal_positivo CHECK (subtotal >= 0),
    CONSTRAINT chk_mes CHECK (mes_orden BETWEEN 1 AND 12)
);

-- Tabla: fct_pagos
-- Tabla de hechos para análisis de pagos
CREATE TABLE IF NOT EXISTS marts.fct_pagos (
    pago_id INTEGER PRIMARY KEY,
    orden_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    metodo_pago_id INTEGER NOT NULL,
    fecha_pago_id DATE NOT NULL,
    
    -- Medidas (métricas)
    monto_pago NUMERIC(10, 2) NOT NULL,
    monto_pagado NUMERIC(10, 2) NOT NULL,
    total_orden NUMERIC(10, 2) NOT NULL,
    
    -- Atributos descriptivos
    metodo_pago_nombre VARCHAR(100),
    estado_pago VARCHAR(50) NOT NULL,
    estado_orden VARCHAR(50),
    pago_completado BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Campos de fecha para particionamiento
    anio_pago INTEGER NOT NULL,
    mes_pago INTEGER NOT NULL,
    mes_completo_pago DATE NOT NULL,
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_monto_pago_positivo CHECK (monto_pago >= 0),
    CONSTRAINT chk_monto_pagado_positivo CHECK (monto_pagado >= 0),
    CONSTRAINT chk_total_orden_positivo CHECK (total_orden >= 0),
    CONSTRAINT chk_mes_pago CHECK (mes_pago BETWEEN 1 AND 12)
);

-- Tabla: fct_resenas
-- Tabla de hechos para análisis de reseñas
CREATE TABLE IF NOT EXISTS marts.fct_resenas (
    resena_id INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    fecha_resena_id DATE NOT NULL,
    
    -- Medidas (métricas)
    calificacion INTEGER NOT NULL,
    
    -- Atributos descriptivos
    comentario TEXT,
    sentimiento_resena VARCHAR(20),
    
    -- Campos de fecha para particionamiento
    anio_resena INTEGER NOT NULL,
    mes_resena INTEGER NOT NULL,
    mes_completo_resena DATE NOT NULL,
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_calificacion CHECK (calificacion BETWEEN 1 AND 5),
    CONSTRAINT chk_sentimiento CHECK (sentimiento_resena IN ('Positiva', 'Neutra', 'Negativa')),
    CONSTRAINT chk_mes_resena CHECK (mes_resena BETWEEN 1 AND 12)
);

-- ============================================================================
-- COMENTARIOS EN TABLAS
-- ============================================================================

COMMENT ON TABLE marts.fct_ventas IS 'Tabla de hechos de ventas - Hecho principal para análisis de ventas';
COMMENT ON TABLE marts.fct_pagos IS 'Tabla de hechos de pagos - Análisis de transacciones de pago';
COMMENT ON TABLE marts.fct_resenas IS 'Tabla de hechos de reseñas - Análisis de satisfacción del cliente';

-- ============================================================================
-- COMENTARIOS EN COLUMNAS CLAVE
-- ============================================================================

COMMENT ON COLUMN marts.fct_ventas.venta_id IS 'ID único de la venta (surrogate key)';
COMMENT ON COLUMN marts.fct_ventas.orden_id IS 'ID de la orden (natural key)';
COMMENT ON COLUMN marts.fct_ventas.usuario_id IS 'Foreign key a dim_usuarios';
COMMENT ON COLUMN marts.fct_ventas.producto_id IS 'Foreign key a dim_productos';
COMMENT ON COLUMN marts.fct_ventas.categoria_id IS 'Foreign key a dim_categorias';
COMMENT ON COLUMN marts.fct_ventas.fecha_venta_id IS 'Foreign key a dim_fecha';

COMMENT ON COLUMN marts.fct_pagos.pago_id IS 'ID único del pago (surrogate key)';
COMMENT ON COLUMN marts.fct_pagos.orden_id IS 'ID de la orden (natural key)';
COMMENT ON COLUMN marts.fct_pagos.usuario_id IS 'Foreign key a dim_usuarios';
COMMENT ON COLUMN marts.fct_pagos.metodo_pago_id IS 'Foreign key a dim_metodos_pago';
COMMENT ON COLUMN marts.fct_pagos.fecha_pago_id IS 'Foreign key a dim_fecha';

COMMENT ON COLUMN marts.fct_resenas.resena_id IS 'ID único de la reseña (surrogate key)';
COMMENT ON COLUMN marts.fct_resenas.usuario_id IS 'Foreign key a dim_usuarios';
COMMENT ON COLUMN marts.fct_resenas.producto_id IS 'Foreign key a dim_productos';
COMMENT ON COLUMN marts.fct_resenas.fecha_resena_id IS 'Foreign key a dim_fecha';

