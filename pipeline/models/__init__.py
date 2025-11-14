"""
Módulo de modelos ORM.
Contiene modelos ORM, enumeraciones y funciones para crear el esquema.
"""

from .models import Base
from .enums import EstadoOrden, EstadoPago
from .create_tables import (
    create_all_tables,
    create_staging_tables,
    create_production_tables
)

# NOTA: Modelos raw (staging) NO se importan aquí.
# Las tablas staging se crean con SQL directo (create_staging_tables.sql)
# y los datos se cargan usando SQL puro (load_raw_data.py).
# Solo se usa ORM para las tablas de producción.

__all__ = [
    'Base',
    'EstadoOrden',
    'EstadoPago',
    # Funciones de creación de tablas
    'create_all_tables',
    'create_staging_tables',
    'create_production_tables',
]

