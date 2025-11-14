"""
Módulo ETL (Extract, Transform, Load).
Contiene funciones para cargar datos desde archivos CSV a PostgreSQL, transformarlos y cargarlos a producción.
"""

from .load_raw_data import load_raw_data
from .transformations import (
    apply_transformations,
    apply_trim,
    normalize_emails,
    remove_duplicates_by_key
)
from .load_to_production import (
    load_to_production,
    load_all_to_production
)
from .pipeline import (
    run_full_pipeline,
    run_staging_load,
    run_transformations,
    run_production_load
)

__all__ = [
    # Carga de datos crudos a staging
    'load_raw_data',
    # Transformaciones
    'apply_transformations',
    'apply_trim',
    'normalize_emails',
    'remove_duplicates_by_key',
    # Carga a producción
    'load_to_production',
    'load_all_to_production',
    # Pipeline modular
    'run_full_pipeline',
    'run_staging_load',
    'run_transformations',
    'run_production_load'
]

