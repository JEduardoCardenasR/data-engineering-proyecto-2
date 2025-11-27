-- ============================================================================
-- Macro: validate_relationship
-- ============================================================================
-- 
-- Macro para validar relaciones entre modelos en dbt
-- 
-- Parámetros:
--   - from_model: Modelo origen (tabla con foreign key)
--   - to_model: Modelo destino (tabla de dimensión)
--   - from_field: Campo en el modelo origen
--   - to_field: Campo en el modelo destino (default: mismo nombre)
--   - where_clause: Condición WHERE opcional
-- 
-- Uso:
--   {{ validate_relationship('fct_ventas', 'dim_usuarios', 'usuario_id') }}
--   {{ validate_relationship('fct_ventas', 'dim_categorias', 'categoria_id', 'categoria_id', 'categoria_id IS NOT NULL') }}
-- ============================================================================

{% macro validate_relationship(from_model, to_model, from_field, to_field=none, where_clause=none) %}
    
    {%- set to_field = to_field if to_field else from_field -%}
    
    SELECT 
        COUNT(*) as orphaned_records
    FROM {{ ref(from_model) }} f
    LEFT JOIN {{ ref(to_model) }} t
        ON f.{{ from_field }} = t.{{ to_field }}
    WHERE t.{{ to_field }} IS NULL
    {%- if where_clause %}
        AND {{ where_clause }}
    {%- endif %}
    
{% endmacro %}

