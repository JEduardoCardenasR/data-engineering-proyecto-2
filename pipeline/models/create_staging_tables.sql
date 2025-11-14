-- ============================================================================
-- Script SQL para crear tablas STAGING (datos crudos)
-- Estas tablas almacenan datos sin IDs primarios ni foreign keys
-- Se utilizan para análisis exploratorio y transformaciones antes de producción
-- ============================================================================

-- Tabla: usuarios_raw
CREATE TABLE IF NOT EXISTS usuarios_raw (
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    dni VARCHAR(20),
    email VARCHAR(255),
    contraseña VARCHAR(255),
    fecha_registro TIMESTAMP
);

-- Tabla: categorias_raw
CREATE TABLE IF NOT EXISTS categorias_raw (
    nombre VARCHAR(100),
    descripcion VARCHAR(255)
);

-- Tabla: productos_raw
CREATE TABLE IF NOT EXISTS productos_raw (
    nombre VARCHAR(255),
    descripcion TEXT,
    precio NUMERIC(10, 2),
    stock INTEGER,
    categoria_id INTEGER
);

-- Tabla: ordenes_raw
CREATE TABLE IF NOT EXISTS ordenes_raw (
    usuario_id INTEGER,
    fecha_orden TIMESTAMP,
    total NUMERIC(10, 2),
    estado VARCHAR(50)
);

-- Tabla: detalle_ordenes_raw
CREATE TABLE IF NOT EXISTS detalle_ordenes_raw (
    orden_id INTEGER,
    producto_id INTEGER,
    cantidad INTEGER,
    precio_unitario NUMERIC(10, 2)
);

-- Tabla: direcciones_envio_raw
CREATE TABLE IF NOT EXISTS direcciones_envio_raw (
    usuario_id INTEGER,
    calle VARCHAR(255),
    ciudad VARCHAR(100),
    departamento VARCHAR(100),
    provincia VARCHAR(100),
    distrito VARCHAR(100),
    estado VARCHAR(100),
    codigo_postal VARCHAR(20),
    pais VARCHAR(100)
);

-- Tabla: carrito_raw
CREATE TABLE IF NOT EXISTS carrito_raw (
    usuario_id INTEGER,
    producto_id INTEGER,
    cantidad INTEGER,
    fecha_agregado TIMESTAMP
);

-- Tabla: metodos_pago_raw
CREATE TABLE IF NOT EXISTS metodos_pago_raw (
    nombre VARCHAR(100),
    descripcion VARCHAR(255)
);

-- Tabla: ordenes_metodos_pago_raw
CREATE TABLE IF NOT EXISTS ordenes_metodos_pago_raw (
    orden_id INTEGER,
    metodo_pago_id INTEGER,
    monto_pagado NUMERIC(10, 2)
);

-- Tabla: resenas_productos_raw
CREATE TABLE IF NOT EXISTS resenas_productos_raw (
    usuario_id INTEGER,
    producto_id INTEGER,
    calificacion INTEGER,
    comentario TEXT,
    fecha TIMESTAMP
);

-- Tabla: historial_pagos_raw
CREATE TABLE IF NOT EXISTS historial_pagos_raw (
    orden_id INTEGER,
    metodo_pago_id INTEGER,
    monto NUMERIC(10, 2),
    fecha_pago TIMESTAMP,
    estado_pago VARCHAR(50)
);

