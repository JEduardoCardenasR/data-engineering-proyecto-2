{% snapshot snap_productos %}

{{
    config(
      target_schema='snapshots',
      unique_key='producto_id',
      strategy='check',
      check_cols=['precio', 'stock', 'estado_stock', 'categoria_id'],
      invalidate_hard_deletes=True,
    )
}}

-- Snapshot SCD Type 2 para productos
-- Rastrea cambios en precio, stock, estado_stock y categoria_id
select
    producto_id,
    nombre,
    descripcion,
    precio,
    stock,
    categoria_id,
    estado_stock,
    categoria_nombre,
    categoria_descripcion,
    total_resenas,
    calificacion_promedio,
    categoria_calificacion,
    porcentaje_resenas_positivas
from {{ ref('dim_productos') }}

{% endsnapshot %}

