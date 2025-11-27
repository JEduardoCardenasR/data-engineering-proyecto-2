-- ============================================================================
-- Script DDL: Crear Índices para Optimización
-- Modelo Físico - Data Warehouse
-- Base de datos: PostgreSQL
-- ============================================================================

-- ============================================================================
-- ÍNDICES PARA TABLAS DE HECHOS
-- ============================================================================

-- Índices para fct_ventas
CREATE INDEX IF NOT EXISTS idx_fct_ventas_usuario_id ON marts.fct_ventas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_fct_ventas_producto_id ON marts.fct_ventas(producto_id);
CREATE INDEX IF NOT EXISTS idx_fct_ventas_categoria_id ON marts.fct_ventas(categoria_id);
CREATE INDEX IF NOT EXISTS idx_fct_ventas_fecha_venta_id ON marts.fct_ventas(fecha_venta_id);
CREATE INDEX IF NOT EXISTS idx_fct_ventas_orden_id ON marts.fct_ventas(orden_id);
CREATE INDEX IF NOT EXISTS idx_fct_ventas_mes_completo ON marts.fct_ventas(mes_completo);
CREATE INDEX IF NOT EXISTS idx_fct_ventas_anio_mes ON marts.fct_ventas(anio_orden, mes_orden);

-- Índice compuesto para consultas comunes de ventas por usuario y fecha
CREATE INDEX IF NOT EXISTS idx_fct_ventas_usuario_fecha ON marts.fct_ventas(usuario_id, fecha_venta_id);

-- Índices para fct_pagos
CREATE INDEX IF NOT EXISTS idx_fct_pagos_orden_id ON marts.fct_pagos(orden_id);
CREATE INDEX IF NOT EXISTS idx_fct_pagos_usuario_id ON marts.fct_pagos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_fct_pagos_metodo_pago_id ON marts.fct_pagos(metodo_pago_id);
CREATE INDEX IF NOT EXISTS idx_fct_pagos_fecha_pago_id ON marts.fct_pagos(fecha_pago_id);
CREATE INDEX IF NOT EXISTS idx_fct_pagos_mes_completo_pago ON marts.fct_pagos(mes_completo_pago);
CREATE INDEX IF NOT EXISTS idx_fct_pagos_estado_pago ON marts.fct_pagos(estado_pago);
CREATE INDEX IF NOT EXISTS idx_fct_pagos_anio_mes ON marts.fct_pagos(anio_pago, mes_pago);

-- Índices para fct_resenas
CREATE INDEX IF NOT EXISTS idx_fct_resenas_usuario_id ON marts.fct_resenas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_fct_resenas_producto_id ON marts.fct_resenas(producto_id);
CREATE INDEX IF NOT EXISTS idx_fct_resenas_fecha_resena_id ON marts.fct_resenas(fecha_resena_id);
CREATE INDEX IF NOT EXISTS idx_fct_resenas_mes_completo_resena ON marts.fct_resenas(mes_completo_resena);
CREATE INDEX IF NOT EXISTS idx_fct_resenas_calificacion ON marts.fct_resenas(calificacion);
CREATE INDEX IF NOT EXISTS idx_fct_resenas_sentimiento ON marts.fct_resenas(sentimiento_resena);

-- ============================================================================
-- ÍNDICES PARA TABLAS DE DIMENSIONES
-- ============================================================================

-- Índices para dim_productos
CREATE INDEX IF NOT EXISTS idx_dim_productos_categoria_id ON marts.dim_productos(categoria_id);
CREATE INDEX IF NOT EXISTS idx_dim_productos_estado_stock ON marts.dim_productos(estado_stock);
CREATE INDEX IF NOT EXISTS idx_dim_productos_calificacion ON marts.dim_productos(calificacion_promedio);

-- Índices para dim_usuarios
CREATE INDEX IF NOT EXISTS idx_dim_usuarios_segmento ON marts.dim_usuarios(segmento_cliente);
CREATE INDEX IF NOT EXISTS idx_dim_usuarios_email ON marts.dim_usuarios(email);
CREATE INDEX IF NOT EXISTS idx_dim_usuarios_fecha_registro ON marts.dim_usuarios(fecha_registro);

-- Índices para dim_categorias
CREATE INDEX IF NOT EXISTS idx_dim_categorias_nombre ON marts.dim_categorias(nombre);

-- Índices para dim_metodos_pago
CREATE INDEX IF NOT EXISTS idx_dim_metodos_pago_nombre ON marts.dim_metodos_pago(nombre);

-- Índices para dim_fecha
CREATE INDEX IF NOT EXISTS idx_dim_fecha_anio ON marts.dim_fecha(anio);
CREATE INDEX IF NOT EXISTS idx_dim_fecha_mes ON marts.dim_fecha(mes);
CREATE INDEX IF NOT EXISTS idx_dim_fecha_anio_mes ON marts.dim_fecha(anio, mes);
CREATE INDEX IF NOT EXISTS idx_dim_fecha_trimestre ON marts.dim_fecha(trimestre);
CREATE INDEX IF NOT EXISTS idx_dim_fecha_mes_completo ON marts.dim_fecha(mes_completo);

-- ============================================================================
-- ÍNDICES PARA TABLAS SCD TYPE 2
-- ============================================================================

-- Índices para dim_productos_scd2
CREATE INDEX IF NOT EXISTS idx_dim_productos_scd2_producto_id ON marts.dim_productos_scd2(producto_id);
CREATE INDEX IF NOT EXISTS idx_dim_productos_scd2_es_actual ON marts.dim_productos_scd2(es_actual);
CREATE INDEX IF NOT EXISTS idx_dim_productos_scd2_fechas ON marts.dim_productos_scd2(fecha_inicio_validez, fecha_fin_validez);
CREATE INDEX IF NOT EXISTS idx_dim_productos_scd2_producto_fechas ON marts.dim_productos_scd2(producto_id, fecha_inicio_validez, fecha_fin_validez);

-- Índices para dim_usuarios_scd2
CREATE INDEX IF NOT EXISTS idx_dim_usuarios_scd2_usuario_id ON marts.dim_usuarios_scd2(usuario_id);
CREATE INDEX IF NOT EXISTS idx_dim_usuarios_scd2_es_actual ON marts.dim_usuarios_scd2(es_actual);
CREATE INDEX IF NOT EXISTS idx_dim_usuarios_scd2_fechas ON marts.dim_usuarios_scd2(fecha_inicio_validez, fecha_fin_validez);
CREATE INDEX IF NOT EXISTS idx_dim_usuarios_scd2_usuario_fechas ON marts.dim_usuarios_scd2(usuario_id, fecha_inicio_validez, fecha_fin_validez);
CREATE INDEX IF NOT EXISTS idx_dim_usuarios_scd2_segmento ON marts.dim_usuarios_scd2(segmento_cliente);

-- ============================================================================
-- COMENTARIOS
-- ============================================================================

COMMENT ON INDEX marts.idx_fct_ventas_usuario_fecha IS 'Índice compuesto para consultas de ventas por usuario y fecha';
COMMENT ON INDEX marts.idx_dim_productos_scd2_producto_fechas IS 'Índice compuesto para consultas históricas de productos';
COMMENT ON INDEX marts.idx_dim_usuarios_scd2_usuario_fechas IS 'Índice compuesto para consultas históricas de usuarios';

