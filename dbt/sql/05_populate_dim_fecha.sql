-- ============================================================================
-- Script DDL: Poblar Tabla de Dimensiones de Fecha
-- Modelo Físico - Data Warehouse
-- Base de datos: PostgreSQL
-- ============================================================================

-- Función para poblar dim_fecha con un rango de fechas
-- Uso: SELECT populate_dim_fecha('2020-01-01'::date, '2030-12-31'::date);

CREATE OR REPLACE FUNCTION populate_dim_fecha(
    fecha_inicio DATE,
    fecha_fin DATE
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO marts.dim_fecha (
        fecha_id,
        anio,
        trimestre,
        mes,
        semana,
        dia,
        dia_semana,
        dia_anio,
        mes_completo,
        trimestre_completo,
        anio_completo,
        nombre_mes,
        nombre_dia_semana,
        es_fin_semana,
        estacion
    )
    SELECT
        fecha::date as fecha_id,
        EXTRACT(YEAR FROM fecha)::INTEGER as anio,
        EXTRACT(QUARTER FROM fecha)::INTEGER as trimestre,
        EXTRACT(MONTH FROM fecha)::INTEGER as mes,
        EXTRACT(WEEK FROM fecha)::INTEGER as semana,
        EXTRACT(DAY FROM fecha)::INTEGER as dia,
        EXTRACT(DOW FROM fecha)::INTEGER as dia_semana,
        EXTRACT(DOY FROM fecha)::INTEGER as dia_anio,
        DATE_TRUNC('month', fecha)::DATE as mes_completo,
        DATE_TRUNC('quarter', fecha)::DATE as trimestre_completo,
        DATE_TRUNC('year', fecha)::DATE as anio_completo,
        TO_CHAR(fecha, 'Month') as nombre_mes,
        TO_CHAR(fecha, 'Day') as nombre_dia_semana,
        CASE WHEN EXTRACT(DOW FROM fecha) IN (0, 6) THEN TRUE ELSE FALSE END as es_fin_semana,
        CASE 
            WHEN EXTRACT(MONTH FROM fecha) IN (12, 1, 2) THEN 'Invierno'
            WHEN EXTRACT(MONTH FROM fecha) IN (3, 4, 5) THEN 'Primavera'
            WHEN EXTRACT(MONTH FROM fecha) IN (6, 7, 8) THEN 'Verano'
            ELSE 'Otoño'
        END as estacion
    FROM generate_series(fecha_inicio, fecha_fin, '1 day'::interval) as fecha
    ON CONFLICT (fecha_id) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- Poblar dim_fecha con un rango por defecto (2020-2030)
-- Ajustar el rango según las necesidades del proyecto
SELECT populate_dim_fecha('2020-01-01'::date, '2030-12-31'::date);

-- Verificar que se pobló correctamente
SELECT 
    COUNT(*) as total_fechas,
    MIN(fecha_id) as fecha_minima,
    MAX(fecha_id) as fecha_maxima
FROM marts.dim_fecha;

