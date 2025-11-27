{{
    config(
        materialized='view'
    )
}}

-- Modelo intermedio que agrega métricas de órdenes por usuario
with usuarios as (
    select * from {{ ref('stg_usuarios') }}
),

ordenes as (
    select * from {{ ref('stg_ordenes') }}
),

usuarios_ordenes as (
    select
        u.usuario_id,
        u.nombre,
        u.apellido,
        u.email,
        u.fecha_registro,
        -- Métricas de órdenes
        count(o.orden_id) as total_ordenes,
        sum(o.total) as total_gastado,
        avg(o.total) as promedio_por_orden,
        min(o.fecha_orden) as primera_orden,
        max(o.fecha_orden) as ultima_orden,
        sum(case when o.estado = 'COMPLETADA' then 1 else 0 end) as ordenes_completadas,
        sum(case when o.estado = 'PENDIENTE' then 1 else 0 end) as ordenes_pendientes
    from usuarios u
    left join ordenes o
        on u.usuario_id = o.usuario_id
    group by
        u.usuario_id,
        u.nombre,
        u.apellido,
        u.email,
        u.fecha_registro
)

select * from usuarios_ordenes

