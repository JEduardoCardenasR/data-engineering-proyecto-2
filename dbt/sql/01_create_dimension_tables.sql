-- ============================================================================
-- Script DDL: Crear Tablas de Dimensiones del Modelo Dimensional
-- Modelo Físico - Data Warehouse
-- Base de datos: PostgreSQL
-- ============================================================================

-- Crear esquema para el data warehouse si no existe
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS snapshots;

-- ============================================================================
-- DIMENSIONES BASE
-- ============================================================================

-- Tabla: dim_fecha
-- Dimensión de tiempo (estática, pre-poblada)
CREATE TABLE IF NOT EXISTS marts.dim_fecha (
    fecha_id DATE PRIMARY KEY,
    anio INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    semana INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL,
    dia_anio INTEGER NOT NULL,
    mes_completo DATE NOT NULL,
    trimestre_completo DATE NOT NULL,
    anio_completo DATE NOT NULL,
    nombre_mes VARCHAR(20),
    nombre_dia_semana VARCHAR(20),
    es_fin_semana BOOLEAN NOT NULL DEFAULT FALSE,
    estacion VARCHAR(20),
    CONSTRAINT chk_mes CHECK (mes BETWEEN 1 AND 12),
    CONSTRAINT chk_dia CHECK (dia BETWEEN 1 AND 31),
    CONSTRAINT chk_trimestre CHECK (trimestre BETWEEN 1 AND 4)
);

-- Tabla: dim_categorias
-- Dimensión de categorías (SCD Type 1)
CREATE TABLE IF NOT EXISTS marts.dim_categorias (
    categoria_id INTEGER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    total_productos INTEGER DEFAULT 0,
    stock_total INTEGER DEFAULT 0,
    precio_promedio NUMERIC(10, 2),
    precio_minimo NUMERIC(10, 2),
    precio_maximo NUMERIC(10, 2),
    productos_agotados INTEGER DEFAULT 0,
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: dim_metodos_pago
-- Dimensión de métodos de pago (SCD Type 1)
CREATE TABLE IF NOT EXISTS marts.dim_metodos_pago (
    metodo_pago_id INTEGER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    total_usos INTEGER DEFAULT 0,
    total_monto_pagado NUMERIC(10, 2) DEFAULT 0,
    promedio_monto_pagado NUMERIC(10, 2),
    monto_minimo NUMERIC(10, 2),
    monto_maximo NUMERIC(10, 2),
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: dim_productos
-- Dimensión de productos (base para SCD)
CREATE TABLE IF NOT EXISTS marts.dim_productos (
    producto_id INTEGER PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    precio NUMERIC(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    estado_stock VARCHAR(20),
    categoria_id INTEGER,
    categoria_nombre VARCHAR(100),
    categoria_descripcion VARCHAR(255),
    total_resenas INTEGER DEFAULT 0,
    calificacion_promedio NUMERIC(3, 2) DEFAULT 0,
    calificacion_minima INTEGER,
    calificacion_maxima INTEGER,
    resenas_positivas INTEGER DEFAULT 0,
    resenas_negativas INTEGER DEFAULT 0,
    resenas_neutras INTEGER DEFAULT 0,
    categoria_calificacion VARCHAR(20),
    porcentaje_resenas_positivas NUMERIC(5, 2) DEFAULT 0,
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_precio_positivo CHECK (precio >= 0),
    CONSTRAINT chk_stock_positivo CHECK (stock >= 0),
    CONSTRAINT chk_calificacion CHECK (calificacion_promedio >= 0 AND calificacion_promedio <= 5)
);

-- Tabla: dim_usuarios
-- Dimensión de usuarios (base para SCD)
CREATE TABLE IF NOT EXISTS marts.dim_usuarios (
    usuario_id INTEGER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    nombre_completo VARCHAR(201) NOT NULL,
    email VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP NOT NULL,
    total_ordenes INTEGER DEFAULT 0,
    total_gastado NUMERIC(10, 2) DEFAULT 0,
    promedio_por_orden NUMERIC(10, 2),
    primera_orden TIMESTAMP,
    ultima_orden TIMESTAMP,
    ordenes_completadas INTEGER DEFAULT 0,
    ordenes_pendientes INTEGER DEFAULT 0,
    segmento_cliente VARCHAR(20),
    anio_registro INTEGER,
    mes_registro INTEGER,
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_total_gastado CHECK (total_gastado >= 0),
    CONSTRAINT chk_segmento CHECK (segmento_cliente IN ('Nuevo', 'Ocasional', 'Regular', 'VIP'))
);

-- ============================================================================
-- DIMENSIONES SCD TYPE 2
-- ============================================================================

-- Tabla: dim_productos_scd2
-- Dimensión de productos con historial completo (SCD Type 2)
CREATE TABLE IF NOT EXISTS marts.dim_productos_scd2 (
    scd_id VARCHAR(50) PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    precio NUMERIC(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    estado_stock VARCHAR(20),
    categoria_id INTEGER,
    categoria_nombre VARCHAR(100),
    categoria_descripcion VARCHAR(255),
    total_resenas INTEGER DEFAULT 0,
    calificacion_promedio NUMERIC(3, 2) DEFAULT 0,
    categoria_calificacion VARCHAR(20),
    porcentaje_resenas_positivas NUMERIC(5, 2) DEFAULT 0,
    fecha_inicio_validez TIMESTAMP NOT NULL,
    fecha_fin_validez TIMESTAMP NOT NULL,
    es_actual BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_precio_scd2 CHECK (precio >= 0),
    CONSTRAINT chk_stock_scd2 CHECK (stock >= 0),
    CONSTRAINT chk_fechas_scd2 CHECK (fecha_fin_validez > fecha_inicio_validez)
);

-- Tabla: dim_usuarios_scd2
-- Dimensión de usuarios con historial completo (SCD Type 2)
CREATE TABLE IF NOT EXISTS marts.dim_usuarios_scd2 (
    scd_id VARCHAR(50) PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    nombre_completo VARCHAR(201) NOT NULL,
    email VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP NOT NULL,
    total_ordenes INTEGER DEFAULT 0,
    total_gastado NUMERIC(10, 2) DEFAULT 0,
    promedio_por_orden NUMERIC(10, 2),
    primera_orden TIMESTAMP,
    ultima_orden TIMESTAMP,
    ordenes_completadas INTEGER DEFAULT 0,
    ordenes_pendientes INTEGER DEFAULT 0,
    segmento_cliente VARCHAR(20),
    anio_registro INTEGER,
    mes_registro INTEGER,
    fecha_inicio_validez TIMESTAMP NOT NULL,
    fecha_fin_validez TIMESTAMP NOT NULL,
    es_actual BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_total_gastado_scd2 CHECK (total_gastado >= 0),
    CONSTRAINT chk_segmento_scd2 CHECK (segmento_cliente IN ('Nuevo', 'Ocasional', 'Regular', 'VIP')),
    CONSTRAINT chk_fechas_usuarios_scd2 CHECK (fecha_fin_validez > fecha_inicio_validez)
);

-- ============================================================================
-- COMENTARIOS EN TABLAS
-- ============================================================================

COMMENT ON TABLE marts.dim_fecha IS 'Dimensión de tiempo estática para análisis temporal';
COMMENT ON TABLE marts.dim_categorias IS 'Dimensión de categorías (SCD Type 1)';
COMMENT ON TABLE marts.dim_metodos_pago IS 'Dimensión de métodos de pago (SCD Type 1)';
COMMENT ON TABLE marts.dim_productos IS 'Dimensión de productos base';
COMMENT ON TABLE marts.dim_usuarios IS 'Dimensión de usuarios base';
COMMENT ON TABLE marts.dim_productos_scd2 IS 'Dimensión de productos con historial (SCD Type 2)';
COMMENT ON TABLE marts.dim_usuarios_scd2 IS 'Dimensión de usuarios con historial (SCD Type 2)';

