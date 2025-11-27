{% snapshot snap_usuarios %}

{{
    config(
      target_schema='snapshots',
      unique_key='usuario_id',
      strategy='check',
      check_cols=['segmento_cliente', 'total_ordenes', 'total_gastado', 'email'],
      invalidate_hard_deletes=True,
    )
}}

-- Snapshot SCD Type 2 para usuarios
-- Rastrea cambios en segmento_cliente, métricas agregadas y email
select
    usuario_id,
    nombre,
    apellido,
    nombre_completo,
    email,
    fecha_registro,
    total_ordenes,
    total_gastado,
    promedio_por_orden,
    primera_orden,
    ultima_orden,
    ordenes_completadas,
    ordenes_pendientes,
    segmento_cliente,
    anio_registro,
    mes_registro
from {{ ref('dim_usuarios') }}

{% endsnapshot %}

