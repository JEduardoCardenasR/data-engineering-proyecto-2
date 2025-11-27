{{
    config(
        materialized='table'
    )
}}

-- Tabla de dimensiones: Usuarios
-- Modelo dimensional siguiendo el esquema estrella de Kimball
with usuarios_ordenes as (
    select * from {{ ref('int_usuarios_ordenes') }}
),

final as (
    select
        -- Clave primaria
        usuario_id,
        
        -- Atributos descriptivos
        nombre,
        apellido,
        concat(nombre, ' ', apellido) as nombre_completo,
        email,
        fecha_registro,
        
        -- Métricas agregadas (SCD Type 1 - se actualizan)
        total_ordenes,
        total_gastado,
        promedio_por_orden,
        primera_orden,
        ultima_orden,
        ordenes_completadas,
        ordenes_pendientes,
        
        -- Campos calculados
        case 
            when total_ordenes = 0 then 'Nuevo'
            when total_ordenes between 1 and 5 then 'Ocasional'
            when total_ordenes between 6 and 20 then 'Regular'
            else 'VIP'
        end as segmento_cliente,
        
        -- Campos de fecha para particionamiento
        extract(year from fecha_registro) as anio_registro,
        extract(month from fecha_registro) as mes_registro
    from usuarios_ordenes
)

select * from final

