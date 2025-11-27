{{
    config(
        materialized='table'
    )
}}

-- Tabla de dimensiones: Fecha
-- Modelo dimensional siguiendo el esquema estrella de Kimball
-- Tabla de fechas para análisis temporal

with fechas as (
    select
        fecha::date as fecha_id,
        extract(year from fecha) as anio,
        extract(quarter from fecha) as trimestre,
        extract(month from fecha) as mes,
        extract(week from fecha) as semana,
        extract(day from fecha) as dia,
        extract(dow from fecha) as dia_semana,
        extract(doy from fecha) as dia_anio,
        date_trunc('month', fecha) as mes_completo,
        date_trunc('quarter', fecha) as trimestre_completo,
        date_trunc('year', fecha) as anio_completo,
        -- Nombres descriptivos
        to_char(fecha, 'Month') as nombre_mes,
        to_char(fecha, 'Day') as nombre_dia_semana,
        -- Indicadores
        case when extract(dow from fecha) in (0, 6) then true else false end as es_fin_semana,
        case when extract(month from fecha) in (12, 1, 2) then 'Invierno'
             when extract(month from fecha) in (3, 4, 5) then 'Primavera'
             when extract(month from fecha) in (6, 7, 8) then 'Verano'
             else 'Otoño' end as estacion
    from (
        select generate_series(
            (select min(fecha_orden)::date from {{ ref('stg_ordenes') }}),
            (select max(fecha_orden)::date from {{ ref('stg_ordenes') }}),
            '1 day'::interval
        ) as fecha
    ) fechas_series
)

select * from fechas

