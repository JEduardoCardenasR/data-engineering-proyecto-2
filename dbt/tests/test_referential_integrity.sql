-- ============================================================================
-- Test SQL: Validación de Integridad Referencial
-- ============================================================================
-- 
-- Este test valida que no hay valores huérfanos en las foreign keys
-- de las tablas de hechos que no existan en las dimensiones.
-- 
-- Ejecutar con: dbt test --select test_referential_integrity
-- ============================================================================

-- Test: Validar que todos los usuario_id en fct_ventas existen en dim_usuarios
SELECT 
    COUNT(*) as registros_huérfanos
FROM {{ ref('fct_ventas') }} fv
LEFT JOIN {{ ref('dim_usuarios') }} du
    ON fv.usuario_id = du.usuario_id
WHERE du.usuario_id IS NULL

