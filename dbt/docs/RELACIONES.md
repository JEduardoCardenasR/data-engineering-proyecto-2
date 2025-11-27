# Relaciones e Integridad Referencial en dbt

Este documento describe cómo se manejan las relaciones entre modelos en dbt para garantizar integridad referencial.

## Estructura de Relaciones

### Modelo Dimensional (Esquema Estrella)

```
                    dim_fecha
                        │
        ┌───────────────┼───────────────┐
        │               │               │
    dim_usuarios    dim_productos   dim_categorias
        │               │               │
        │               └───────┬───────┘
        │                       │
        └───────────┬───────────┘
                    │
            ┌───────┼───────┐
            │       │       │
        fct_ventas  │   fct_resenas
                    │
                fct_pagos
```

## Relaciones Definidas

### Tablas de Hechos → Dimensiones

#### fct_ventas
- `usuario_id` → `dim_usuarios.usuario_id`
- `producto_id` → `dim_productos.producto_id`
- `categoria_id` → `dim_categorias.categoria_id` (nullable)
- `fecha_venta_id` → `dim_fecha.fecha_id`

#### fct_pagos
- `usuario_id` → `dim_usuarios.usuario_id`
- `metodo_pago_id` → `dim_metodos_pago.metodo_pago_id`
- `fecha_pago_id` → `dim_fecha.fecha_id`

#### fct_resenas
- `usuario_id` → `dim_usuarios.usuario_id`
- `producto_id` → `dim_productos.producto_id`
- `fecha_resena_id` → `dim_fecha.fecha_id`

### Tablas de Dimensiones → Dimensiones

#### dim_productos
- `categoria_id` → `dim_categorias.categoria_id` (nullable)

## Tests de Integridad Referencial

### Tests en schema.yml

Los tests de `relationships` se definen en:
- `models/marts/schema.yml` - Tests a nivel de columna
- `models/marts/relationships.yml` - Tests a nivel de modelo

### Ejemplo de Test

```yaml
- name: usuario_id
  description: "ID del usuario (Foreign key a dim_usuarios)"
  tests:
    - relationships:
        to: ref('dim_usuarios')
        field: usuario_id
```

### Ejecutar Tests

```bash
# Instalar paquetes de dbt (si se usa dbt_utils)
dbt deps

# Ejecutar todos los tests de relaciones
dbt test --select relationships

# Ejecutar tests de un modelo específico
dbt test --select fct_ventas

# Ejecutar todos los tests
dbt test
```

## Macro de Validación

Se proporciona una macro `validate_relationship` para validar relaciones personalizadas:

```sql
{{ validate_relationship('fct_ventas', 'dim_usuarios', 'usuario_id') }}
```

## Manejo de Valores Nulos

Algunas relaciones permiten valores NULL:
- `fct_ventas.categoria_id` puede ser NULL
- `dim_productos.categoria_id` puede ser NULL

Los tests incluyen cláusulas `where` para manejar estos casos:

```yaml
tests:
  - relationships:
      to: ref('dim_categorias')
      field: categoria_id
      config:
        where: "categoria_id IS NOT NULL"
```

## Orden de Ejecución

dbt garantiza el orden correcto de ejecución mediante:
1. **Dependencias implícitas**: `ref()` y `source()` crean dependencias automáticas
2. **Tests de relaciones**: Se ejecutan después de que los modelos están listos
3. **Validación**: Los tests fallan si hay valores huérfanos

## Mejores Prácticas

1. **Siempre usar `ref()`**: Para referenciar otros modelos en dbt
2. **Definir tests**: Agregar tests de relationships para todas las foreign keys
3. **Manejar NULLs**: Incluir cláusulas `where` para campos nullable
4. **Severidad de tests**: Usar `error` para relaciones críticas, `warn` para opcionales
5. **Documentar relaciones**: Mantener este documento actualizado

## Troubleshooting

### Test falla: "Foreign key not found"

1. Verificar que el modelo de dimensión existe y tiene datos
2. Verificar que el campo de foreign key tiene el nombre correcto
3. Verificar que hay datos en la dimensión antes de ejecutar el test

### Test falla: "Orphaned records found"

1. Revisar los datos fuente en staging
2. Verificar que los procesos ETL están cargando datos correctamente
3. Revisar los logs de dbt para identificar registros específicos

## Referencias

- [dbt Relationships Test](https://docs.getdbt.com/reference/resource-properties/tests#relationships)
- [dbt_utils relationships_where](https://github.com/dbt-labs/dbt-utils#relationships_where-source)
- [Modelo Dimensional Kimball](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/)

