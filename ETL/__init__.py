"""
Módulo ETL (Extract, Transform, Load).
Contiene funciones para cargar datos desde archivos CSV a PostgreSQL.
"""

from .load_data import load_data

__all__ = ['load_data']

