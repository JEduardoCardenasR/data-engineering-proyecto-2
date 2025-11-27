-- ============================================================================
-- Script DDL: Crear Foreign Keys (Claves Foráneas)
-- Modelo Físico - Data Warehouse
-- Base de datos: PostgreSQL
-- Nota: Las foreign keys son opcionales en data warehouses para performance
-- ============================================================================

-- ============================================================================
-- FOREIGN KEYS PARA TABLAS DE HECHOS
-- ============================================================================

-- Foreign keys para fct_ventas
-- Nota: Comentadas por defecto para mejor performance en carga de datos
-- Descomentar si se requiere integridad referencial estricta

/*
ALTER TABLE marts.fct_ventas
    ADD CONSTRAINT fk_fct_ventas_usuario 
    FOREIGN KEY (usuario_id) REFERENCES marts.dim_usuarios(usuario_id);

ALTER TABLE marts.fct_ventas
    ADD CONSTRAINT fk_fct_ventas_producto 
    FOREIGN KEY (producto_id) REFERENCES marts.dim_productos(producto_id);

ALTER TABLE marts.fct_ventas
    ADD CONSTRAINT fk_fct_ventas_categoria 
    FOREIGN KEY (categoria_id) REFERENCES marts.dim_categorias(categoria_id);

ALTER TABLE marts.fct_ventas
    ADD CONSTRAINT fk_fct_ventas_fecha 
    FOREIGN KEY (fecha_venta_id) REFERENCES marts.dim_fecha(fecha_id);
*/

-- Foreign keys para fct_pagos
/*
ALTER TABLE marts.fct_pagos
    ADD CONSTRAINT fk_fct_pagos_usuario 
    FOREIGN KEY (usuario_id) REFERENCES marts.dim_usuarios(usuario_id);

ALTER TABLE marts.fct_pagos
    ADD CONSTRAINT fk_fct_pagos_metodo_pago 
    FOREIGN KEY (metodo_pago_id) REFERENCES marts.dim_metodos_pago(metodo_pago_id);

ALTER TABLE marts.fct_pagos
    ADD CONSTRAINT fk_fct_pagos_fecha 
    FOREIGN KEY (fecha_pago_id) REFERENCES marts.dim_fecha(fecha_id);
*/

-- Foreign keys para fct_resenas
/*
ALTER TABLE marts.fct_resenas
    ADD CONSTRAINT fk_fct_resenas_usuario 
    FOREIGN KEY (usuario_id) REFERENCES marts.dim_usuarios(usuario_id);

ALTER TABLE marts.fct_resenas
    ADD CONSTRAINT fk_fct_resenas_producto 
    FOREIGN KEY (producto_id) REFERENCES marts.dim_productos(producto_id);

ALTER TABLE marts.fct_resenas
    ADD CONSTRAINT fk_fct_resenas_fecha 
    FOREIGN KEY (fecha_resena_id) REFERENCES marts.dim_fecha(fecha_id);
*/

-- ============================================================================
-- FOREIGN KEYS PARA TABLAS DE DIMENSIONES
-- ============================================================================

-- Foreign key para dim_productos -> dim_categorias
/*
ALTER TABLE marts.dim_productos
    ADD CONSTRAINT fk_dim_productos_categoria 
    FOREIGN KEY (categoria_id) REFERENCES marts.dim_categorias(categoria_id);
*/

-- ============================================================================
-- NOTAS SOBRE FOREIGN KEYS EN DATA WAREHOUSES
-- ============================================================================

-- En data warehouses, las foreign keys a menudo se omiten por:
-- 1. Performance: Las FK agregan overhead en operaciones de carga masiva
-- 2. Flexibilidad: Permiten cargar datos en cualquier orden
-- 3. ETL: Los procesos ETL validan la integridad antes de cargar
-- 
-- Si se requiere integridad referencial, descomentar las FK arriba.
-- Se recomienda crear índices en las columnas FK antes de agregar las constraints.

