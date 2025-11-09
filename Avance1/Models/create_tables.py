"""
Módulo para crear todas las tablas en PostgreSQL usando SQLAlchemy ORM.
Utiliza los modelos definidos en models.py.
"""

import sys

# Import PathManager usando import relativo (Models y Utils están en el mismo nivel: Avance1/)
try:
    from ..Utils.path_manager import PathManager
except ImportError:
    # Si falla el import relativo (ej: ejecutado como script), usar import absoluto
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    avance1_dir = os.path.dirname(current_dir)
    utils_dir = os.path.join(avance1_dir, 'Utils')
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    from path_manager import PathManager

# PathManager maneja toda la configuración de paths
path_manager = PathManager.get_instance()
path_manager.setup_sys_path()

# Import desde el mismo directorio (funciona tanto como módulo como script)
try:
    from .models import Base
    from Database.db_connector import DBConnector
except ImportError:
    # Si falla el import relativo, usar import absoluto
    from models import Base
    from Database.db_connector import DBConnector


def create_all_tables():
    """
    Crea todas las tablas en la base de datos PostgreSQL usando SQLAlchemy ORM.
    Utiliza el DBConnector con patrón Singleton para obtener la conexión.
    """
    print("CREANDO ESQUEMA DE BASE DE DATOS CON SQLALCHEMY ORM")
    
    # Obtener la instancia única del DBConnector
    db = DBConnector.get_instance()
    engine = db.get_engine()
    
    try:
        # Crear todas las tablas definidas en los modelos
        Base.metadata.create_all(engine)
        
        print("\nTodas las tablas creadas exitosamente:")
        
    except Exception as e:
        print(f"\nError al crear las tablas: {str(e)}")
        raise


if __name__ == "__main__":
    create_all_tables()