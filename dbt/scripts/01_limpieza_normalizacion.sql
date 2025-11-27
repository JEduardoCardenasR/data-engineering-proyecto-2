-- ============================================================================
-- Script SQL de Referencia: Limpieza y Normalización de Datos
-- Este script muestra las transformaciones aplicadas en los modelos de staging
-- ============================================================================
-- 
-- Este archivo documenta las técnicas de limpieza y normalización utilizadas
-- en los modelos de staging (stg_*). No se ejecuta directamente, es referencia.
-- 
-- Las transformaciones reales están en: models/staging/stg_*.sql
-- ============================================================================

-- ============================================================================
-- 1. LIMPIEZA DE TEXTO
-- ============================================================================

-- Eliminar espacios al inicio y final
SELECT TRIM(campo) FROM tabla;

-- Convertir a mayúsculas/minúsculas
SELECT UPPER(campo) FROM tabla;  -- Para nombres propios, estados
SELECT LOWER(campo) FROM tabla;  -- Para emails

-- Eliminar espacios múltiples
SELECT REGEXP_REPLACE(TRIM(campo), '\s+', ' ', 'g') FROM tabla;

-- Ejemplo combinado: Limpieza de nombres
SELECT 
    REGEXP_REPLACE(TRIM(UPPER(nombre)), '\s+', ' ', 'g') as nombre_limpio
FROM usuarios;

-- ============================================================================
-- 2. NORMALIZACIÓN DE FORMATOS
-- ============================================================================

-- Normalización de DNI: Solo números
SELECT REGEXP_REPLACE(TRIM(dni), '[^0-9]', '', 'g') as dni_normalizado
FROM usuarios;

-- Normalización de Email: Lowercase y validación básica
SELECT 
    LOWER(TRIM(email)) as email_normalizado,
    CASE 
        WHEN email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' 
        THEN TRUE 
        ELSE FALSE 
    END as email_valido
FROM usuarios;

-- Normalización de Código Postal: Solo alfanuméricos
SELECT UPPER(REGEXP_REPLACE(TRIM(codigo_postal), '[^A-Z0-9]', '', 'g')) as codigo_postal_normalizado
FROM direcciones;

-- ============================================================================
-- 3. NORMALIZACIÓN NUMÉRICA
-- ============================================================================

-- Redondear a 2 decimales
SELECT ROUND(CAST(precio AS NUMERIC), 2) as precio_normalizado
FROM productos;

-- Validar valores positivos
SELECT 
    CASE 
        WHEN precio < 0 THEN 0
        ELSE precio
    END as precio_validado
FROM productos;

-- Convertir a entero
SELECT CAST(cantidad AS INTEGER) as cantidad_entera
FROM detalle_ordenes;

-- ============================================================================
-- 4. NORMALIZACIÓN DE FECHAS
-- ============================================================================

-- Usar fecha actual si es nula
SELECT 
    CASE 
        WHEN fecha_orden IS NULL THEN CURRENT_TIMESTAMP
        ELSE fecha_orden
    END as fecha_normalizada
FROM ordenes;

-- Extraer componentes de fecha
SELECT 
    EXTRACT(YEAR FROM fecha) as anio,
    EXTRACT(MONTH FROM fecha) as mes,
    EXTRACT(DAY FROM fecha) as dia,
    DATE_TRUNC('month', fecha) as mes_completo
FROM ordenes;

-- ============================================================================
-- 5. NORMALIZACIÓN DE ESTADOS/VALORES CATEGÓRICOS
-- ============================================================================

-- Normalizar estados a valores estándar
SELECT 
    CASE 
        WHEN TRIM(UPPER(estado)) IN ('COMPLETADA', 'COMPLETADO', 'COMPLETA') THEN 'COMPLETADA'
        WHEN TRIM(UPPER(estado)) IN ('PENDIENTE', 'PENDIENTE') THEN 'PENDIENTE'
        WHEN TRIM(UPPER(estado)) IN ('CANCELADA', 'CANCELADO', 'CANCEL') THEN 'CANCELADA'
        WHEN estado IS NULL OR TRIM(estado) = '' THEN 'PENDIENTE'
        ELSE TRIM(UPPER(estado))
    END as estado_normalizado
FROM ordenes;

-- ============================================================================
-- 6. MANEJO DE VALORES NULOS
-- ============================================================================

-- Reemplazar NULL con valor por defecto
SELECT COALESCE(descripcion, 'Sin descripción') as descripcion_final
FROM productos;

-- Reemplazar NULL con 'N/A' para campos opcionales
SELECT COALESCE(departamento, 'N/A') as departamento_final
FROM direcciones;

-- ============================================================================
-- 7. VALIDACIÓN DE RANGOS
-- ============================================================================

-- Validar calificaciones entre 1 y 5
SELECT 
    CASE 
        WHEN calificacion < 1 THEN 1
        WHEN calificacion > 5 THEN 5
        ELSE CAST(calificacion AS INTEGER)
    END as calificacion_validada
FROM resenas;

-- ============================================================================
-- 8. FLAGS DE CALIDAD DE DATOS
-- ============================================================================

-- Crear flags para identificar problemas de calidad
SELECT 
    usuario_id,
    nombre,
    email,
    -- Flags de validación
    CASE 
        WHEN email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' 
        THEN FALSE 
        ELSE TRUE 
    END as email_invalido,
    CASE 
        WHEN nombre IS NULL OR TRIM(nombre) = '' 
        THEN TRUE 
        ELSE FALSE 
    END as nombre_incompleto
FROM usuarios;

-- ============================================================================
-- 9. FILTROS DE INTEGRIDAD
-- ============================================================================

-- Filtrar registros con datos mínimos requeridos
SELECT *
FROM usuarios
WHERE nombre IS NOT NULL 
  AND apellido IS NOT NULL
  AND dni IS NOT NULL
  AND email IS NOT NULL;

-- Filtrar valores inválidos
SELECT *
FROM productos
WHERE precio >= 0
  AND stock >= 0
  AND nombre IS NOT NULL
  AND TRIM(nombre) != '';

-- ============================================================================
-- 10. EJEMPLO COMPLETO: Limpieza de Usuarios
-- ============================================================================

WITH source AS (
    SELECT * FROM usuarios_raw
),
renamed AS (
    SELECT
        usuario_id,
        -- Limpieza de nombres
        REGEXP_REPLACE(TRIM(UPPER(nombre)), '\s+', ' ', 'g') as nombre,
        REGEXP_REPLACE(TRIM(UPPER(apellido)), '\s+', ' ', 'g') as apellido,
        -- Limpieza de DNI
        REGEXP_REPLACE(TRIM(dni), '[^0-9]', '', 'g') as dni,
        -- Limpieza de email
        LOWER(TRIM(email)) as email,
        -- Normalización de fecha
        COALESCE(fecha_registro, CURRENT_TIMESTAMP) as fecha_registro
    FROM source
),
final AS (
    SELECT
        usuario_id,
        nombre,
        apellido,
        dni,
        email,
        fecha_registro,
        -- Validaciones
        CASE 
            WHEN email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' 
            THEN TRUE 
            ELSE FALSE 
        END as email_valido,
        CASE 
            WHEN LENGTH(REGEXP_REPLACE(TRIM(dni), '[^0-9]', '', 'g')) >= 8 
            THEN TRUE 
            ELSE FALSE 
        END as dni_valido
    FROM renamed
    WHERE nombre IS NOT NULL 
      AND apellido IS NOT NULL
      AND dni IS NOT NULL
      AND email IS NOT NULL
)
SELECT * FROM final;

