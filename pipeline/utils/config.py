"""
Configuración centralizada del proceso ETL.
Todos los valores configurables del proyecto están aquí.
"""

import os


class ETLConfig:
    """
    Configuración centralizada para el proceso ETL.
    Todos los valores hardcodeados deben estar aquí.
    """
    
    # ==================== PATHS ====================
    # Directorios relativos desde la raíz del proyecto
    CSV_DIR = 'data/CSV'
    SQL_DIR = 'data/sql'
    
    # ==================== PARÁMETROS DE CARGA DE DATOS ====================
    # Encoding para archivos CSV
    CSV_ENCODING = 'utf-8'
    
    # Nota: Los siguientes parámetros ya no se usan con COPY de PostgreSQL:
    # - CHUNK_SIZE: COPY procesa todos los datos de una vez (más eficiente)
    # - DB_INSERT_METHOD: COPY es el método nativo más rápido
    # - DB_IF_EXISTS: COPY siempre agrega datos (append implícito)
    
    # ==================== CONFIGURACIÓN DE BASE DE DATOS ====================
    # (Estos valores se pueden leer del .env si es necesario)
    # Por ahora se usan los del DBConnector
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    @classmethod
    def get_csv_dir_path(cls, project_root: str) -> str:
        """
        Retorna la ruta completa del directorio CSV.
        
        Args:
            project_root: Ruta raíz del proyecto
            
        Returns:
            str: Ruta completa al directorio CSV
        """
        return os.path.join(project_root, cls.CSV_DIR)
    
    @classmethod
    def get_sql_dir_path(cls, project_root: str) -> str:
        """
        Retorna la ruta completa del directorio SQL.
        
        Args:
            project_root: Ruta raíz del proyecto
            
        Returns:
            str: Ruta completa al directorio SQL
        """
        return os.path.join(project_root, cls.SQL_DIR)
