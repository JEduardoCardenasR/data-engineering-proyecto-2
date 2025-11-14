"""
Módulo para gestionar paths del proyecto de manera centralizada.
Implementa el patrón Singleton con caché para evitar recálculos.
"""

import os
import sys
from typing import Optional

# Import configuración centralizada
try:
    from .config import ETLConfig
except ImportError:
    from config import ETLConfig


class PathManager:
    """
    Singleton para gestionar paths del proyecto.
    Evita duplicación de código y recálculos innecesarios.
    """
    
    _instance: Optional['PathManager'] = None
    _project_root: Optional[str] = None
    _current_dir: Optional[str] = None
    _csv_dir: Optional[str] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Implementa el patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(PathManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa los paths solo una vez"""
        if not PathManager._initialized:
            # Calcular project_root: utils -> pipeline -> raíz del proyecto
            current_file = os.path.abspath(__file__)
            PathManager._current_dir = os.path.dirname(current_file)  # pipeline/utils/
            pipeline_dir = os.path.dirname(PathManager._current_dir)    # pipeline/
            PathManager._project_root = os.path.dirname(pipeline_dir)   # raíz del proyecto
            # Calcular CSV directory usando configuración centralizada
            # Importar ETLConfig directamente (sin caché de módulo)
            from .config import ETLConfig
            PathManager._csv_dir = ETLConfig.get_csv_dir_path(PathManager._project_root)
            PathManager._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'PathManager':
        """
        Obtiene la instancia única del PathManager.
        
        Returns:
            PathManager: La única instancia del PathManager
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_project_root(self) -> str:
        """
        Retorna la ruta raíz del proyecto.
        
        Returns:
            str: Ruta absoluta a la raíz del proyecto
        """
        return PathManager._project_root
    
    def get_current_dir(self) -> str:
        """
        Retorna el directorio actual (Utils).
        
        Returns:
            str: Ruta absoluta al directorio Utils
        """
        return PathManager._current_dir
    
    def get_csv_dir(self) -> str:
        """
        Retorna el directorio donde se encuentran los archivos CSV.
        
        Returns:
            str: Ruta absoluta al directorio data/CSV
        """
        return PathManager._csv_dir
    
    def get_csv_path(self, file_name: str) -> str:
        """
        Retorna la ruta completa de un archivo CSV.
        
        Args:
            file_name: Nombre del archivo CSV (ej: '2.Usuarios.csv')
            
        Returns:
            str: Ruta absoluta al archivo CSV
        """
        return os.path.join(PathManager._csv_dir, file_name)
    
    def setup_sys_path(self) -> None:
        """
        Configura sys.path con project_root y current_dir.
        Útil para imports en los módulos.
        """
        if PathManager._project_root not in sys.path:
            sys.path.append(PathManager._project_root)
        
        if PathManager._current_dir not in sys.path:
            sys.path.insert(0, PathManager._current_dir)

