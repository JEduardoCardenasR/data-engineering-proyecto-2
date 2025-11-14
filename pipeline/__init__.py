"""
Paquete pipeline - Sistema ETL para carga de datos a PostgreSQL.

Estructura:
- models: Modelos ORM, enumeraciones y creación de esquema
- etl: Proceso de carga de datos desde CSV (con staging)
- utils: Utilidades (PathManager, Config, clean_column_name)
"""

from .models import Base, EstadoOrden, EstadoPago, create_all_tables, create_staging_tables, create_production_tables
from .etl import load_raw_data, load_all_to_production, run_full_pipeline
from .utils import PathManager, ETLConfig, clean_column_name

__all__ = [
    # Models
    'Base',
    'EstadoOrden',
    'EstadoPago',
    'create_all_tables',
    'create_staging_tables',
    'create_production_tables',
    # ETL
    'load_raw_data',
    'load_all_to_production',
    'run_full_pipeline',
    # Utils
    'PathManager',
    'ETLConfig',
    'clean_column_name'
]
