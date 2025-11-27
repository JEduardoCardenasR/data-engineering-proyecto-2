{{
    config(
        materialized='table'
    )
}}

-- Tabla de hechos: Reseñas
-- Modelo dimensional siguiendo el esquema estrella de Kimball
with resenas as (
    select * from {{ ref('stg_resenas_productos') }}
),

final as (
    select
        -- Claves foráneas a dimensiones
        resena_id,
        usuario_id,
        producto_id,
        fecha::date as fecha_resena_id,
        
        -- Medidas (métricas)
        calificacion,
        
        -- Atributos descriptivos
        comentario,
        sentimiento_resena,
        
        -- Campos de fecha para particionamiento
        anio_resena,
        mes_resena,
        date_trunc('month', fecha) as mes_completo_resena
    from resenas
)

select * from final

