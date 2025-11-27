# Guía de Queries para Analistas

Esta guía proporciona queries optimizadas y ejemplos para responder a las preguntas de negocio más comunes.

## 📊 Vistas Analíticas Disponibles

El proyecto incluye vistas pre-agregadas optimizadas para análisis rápidos:

- `vw_ventas_resumen` - Resumen de ventas con todas las dimensiones
- `vw_clientes_activos` - Análisis de comportamiento de clientes
- `vw_productos_performance` - Performance de productos
- `vw_ventas_temporales` - Análisis temporal con tendencias
- `vw_pagos_resumen` - Resumen de pagos y transacciones

## 🎯 Queries por Categoría

### 📈 VENTAS

#### 1. Productos más vendidos por volumen
```sql
SELECT 
    producto_nombre,
    categoria_nombre,
    total_unidades_vendidas,
    total_ventas,
    total_ordenes
FROM marts.vw_productos_performance
ORDER BY total_unidades_vendidas DESC
LIMIT 10;
```

#### 2. Ticket promedio por orden
```sql
SELECT 
    AVG(ticket_promedio) as ticket_promedio_global,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ticket_promedio) as ticket_mediano
FROM marts.vw_ventas_resumen
WHERE total_ordenes > 0;
```

#### 3. Categorías con mayor número de productos vendidos
```sql
SELECT 
    categoria_nombre,
    COUNT(DISTINCT producto_id) as total_productos,
    SUM(total_unidades_vendidas) as unidades_vendidas,
    SUM(total_ventas) as revenue_total
FROM marts.vw_ventas_resumen
GROUP BY categoria_nombre
ORDER BY unidades_vendidas DESC;
```

#### 4. Día de la semana con más ventas
```sql
SELECT 
    nombre_dia_semana,
    SUM(total_ventas) as ventas_totales,
    AVG(total_ventas) as ventas_promedio,
    COUNT(DISTINCT fecha_id) as dias_analizados
FROM marts.vw_ventas_temporales
GROUP BY nombre_dia_semana, dia_semana
ORDER BY ventas_totales DESC;
```

#### 5. Órdenes por mes y variación
```sql
SELECT 
    anio,
    mes,
    nombre_mes,
    SUM(total_ordenes) as ordenes_mes,
    LAG(SUM(total_ordenes)) OVER (ORDER BY anio, mes) as ordenes_mes_anterior,
    CASE 
        WHEN LAG(SUM(total_ordenes)) OVER (ORDER BY anio, mes) > 0
        THEN ((SUM(total_ordenes) - LAG(SUM(total_ordenes)) OVER (ORDER BY anio, mes)) 
              / LAG(SUM(total_ordenes)) OVER (ORDER BY anio, mes)) * 100
        ELSE NULL
    END as variacion_pct
FROM marts.vw_ventas_temporales
GROUP BY anio, mes, nombre_mes
ORDER BY anio, mes;
```

### 💳 PAGOS Y TRANSACCIONES

#### 6. Métodos de pago más utilizados
```sql
SELECT 
    metodo_pago_nombre,
    total_pagos,
    total_ordenes_pagadas,
    total_recaudado,
    monto_promedio_pago,
    tasa_exito_pct
FROM marts.vw_pagos_resumen
GROUP BY metodo_pago_nombre, metodo_pago_id
ORDER BY total_pagos DESC;
```

#### 7. Monto promedio por método de pago
```sql
SELECT 
    metodo_pago_nombre,
    AVG(monto_promedio_pago) as monto_promedio,
    MIN(monto_minimo) as monto_minimo,
    MAX(monto_maximo) as monto_maximo
FROM marts.vw_pagos_resumen
GROUP BY metodo_pago_nombre
ORDER BY monto_promedio DESC;
```

#### 8. Pagos en estado Procesando o Fallido
```sql
SELECT 
    estado_pago,
    COUNT(*) as total_pagos,
    SUM(monto_pago) as monto_total
FROM marts.fct_pagos
WHERE estado_pago IN ('PROCESANDO', 'RECHAZADO')
GROUP BY estado_pago;
```

#### 9. Monto total recaudado por mes
```sql
SELECT 
    anio,
    mes,
    nombre_mes,
    SUM(total_recaudado) as recaudacion_total,
    COUNT(DISTINCT metodo_pago_id) as metodos_utilizados
FROM marts.vw_pagos_resumen
GROUP BY anio, mes, nombre_mes
ORDER BY anio, mes;
```

### 👥 USUARIOS

#### 10. Usuarios registrados por mes
```sql
SELECT 
    anio_registro,
    mes_registro,
    COUNT(*) as usuarios_registrados,
    SUM(CASE WHEN total_ordenes > 0 THEN 1 ELSE 0 END) as usuarios_con_compras
FROM marts.dim_usuarios
GROUP BY anio_registro, mes_registro
ORDER BY anio_registro DESC, mes_registro DESC;
```

#### 11. Usuarios con más de una orden
```sql
SELECT 
    COUNT(*) as total_usuarios,
    AVG(total_ordenes) as promedio_ordenes,
    MAX(total_ordenes) as max_ordenes
FROM marts.vw_clientes_activos
WHERE total_ordenes > 1;
```

#### 12. Usuarios sin compras
```sql
SELECT 
    COUNT(*) as usuarios_sin_compras,
    AVG(dias_como_cliente) as dias_promedio_sin_comprar
FROM marts.vw_clientes_activos
WHERE estado_cliente = 'Nunca Compró';
```

#### 13. Usuarios que más han gastado
```sql
SELECT 
    nombre_completo,
    segmento_cliente,
    total_gastado,
    total_ordenes,
    promedio_por_orden,
    ultima_orden
FROM marts.vw_clientes_activos
ORDER BY total_gastado DESC
LIMIT 20;
```

#### 14. Usuarios que han dejado reseñas
```sql
SELECT 
    COUNT(DISTINCT usuario_id) as usuarios_con_resenas,
    AVG(total_resenas) as promedio_resenas_por_usuario,
    AVG(calificacion_promedio_dada) as calificacion_promedio
FROM marts.vw_clientes_activos
WHERE total_resenas > 0;
```

### 📦 PRODUCTOS Y STOCK

#### 15. Productos con alto stock pero bajas ventas
```sql
SELECT 
    producto_nombre,
    categoria_nombre,
    stock,
    total_unidades_vendidas,
    ratio_rotacion,
    categoria_performance
FROM marts.vw_productos_performance
WHERE stock > 50 
  AND total_unidades_vendidas < 10
ORDER BY stock DESC;
```

#### 16. Productos fuera de stock
```sql
SELECT 
    producto_nombre,
    categoria_nombre,
    precio,
    total_resenas,
    calificacion_promedio,
    ultima_venta
FROM marts.vw_productos_performance
WHERE estado_stock = 'Agotado'
ORDER BY ultima_venta DESC;
```

#### 17. Productos peor calificados
```sql
SELECT 
    producto_nombre,
    categoria_nombre,
    calificacion_promedio,
    total_resenas,
    categoria_calificacion,
    total_revenue
FROM marts.vw_productos_performance
WHERE total_resenas > 0
ORDER BY calificacion_promedio ASC
LIMIT 20;
```

#### 18. Productos con mayor cantidad de reseñas
```sql
SELECT 
    producto_nombre,
    categoria_nombre,
    total_resenas,
    calificacion_promedio,
    porcentaje_resenas_positivas,
    categoria_calificacion
FROM marts.vw_productos_performance
WHERE total_resenas > 0
ORDER BY total_resenas DESC
LIMIT 20;
```

#### 19. Categoría con mayor valor económico vendido
```sql
SELECT 
    categoria_nombre,
    COUNT(DISTINCT producto_id) as total_productos,
    SUM(total_revenue) as revenue_total,
    SUM(total_unidades_vendidas) as unidades_vendidas,
    AVG(calificacion_promedio) as calificacion_promedio_categoria
FROM marts.vw_productos_performance
GROUP BY categoria_nombre
ORDER BY revenue_total DESC;
```

## 🚀 Mejores Prácticas

### 1. Usar Vistas Analíticas
Siempre que sea posible, usar las vistas analíticas (`vw_*`) en lugar de las tablas base. Están optimizadas y pre-agregadas.

### 2. Filtrar por Fechas
Para análisis temporales, siempre filtrar por rango de fechas:
```sql
WHERE fecha_id BETWEEN '2024-01-01' AND '2024-12-31'
```

### 3. Limitar Resultados
Usar `LIMIT` en queries exploratorias para mejorar performance:
```sql
ORDER BY total_ventas DESC
LIMIT 10
```

### 4. Índices Disponibles
Las tablas tienen índices en:
- Foreign keys (usuario_id, producto_id, etc.)
- Campos de fecha (fecha_id, mes_completo, etc.)
- Campos de búsqueda frecuente (segmento_cliente, estado_stock, etc.)

### 5. Usar Agregaciones
Para métricas agregadas, usar las vistas que ya incluyen cálculos:
- `vw_ventas_temporales` tiene promedios móviles
- `vw_productos_performance` tiene ratios de rotación
- `vw_clientes_activos` tiene días desde última compra

## 📝 Notas de Performance

- Las vistas están materializadas como `view` para siempre tener datos actualizados
- Para análisis muy pesados, considerar crear tablas materializadas
- Los índices están optimizados para las queries más comunes
- Usar `EXPLAIN ANALYZE` para verificar el plan de ejecución

