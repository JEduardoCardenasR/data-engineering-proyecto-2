"""
Módulo para crear tablas en PostgreSQL.
- Tablas staging: se crean con SQL directo (sin primary keys)
- Tablas producción: se crean con SQLAlchemy ORM (con primary keys y foreign keys)
"""

import os
import sys
from sqlalchemy import text

# Import PathManager usando import relativo (models y utils están en el mismo nivel: pipeline/)
try:
    from ..utils.path_manager import PathManager
except ImportError:
    # Si falla el import relativo (ej: ejecutado como script), usar import absoluto
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline_dir = os.path.dirname(current_dir)
    utils_dir = os.path.join(pipeline_dir, 'utils')
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    from path_manager import PathManager

# PathManager maneja toda la configuración de paths
path_manager = PathManager.get_instance()
path_manager.setup_sys_path()

# Import desde el mismo directorio (funciona tanto como módulo como script)
try:
    from .models import Base
    from .models import (
        Usuario,
        Categoria,
        Producto,
        Orden,
        DetalleOrden,
        DireccionEnvio,
        Carrito,
        MetodoPago,
        OrdenMetodoPago,
        ResenaProducto,
        HistorialPago
    )
    from database.db_connector import DBConnector
except ImportError:
    # Si falla el import relativo, usar import absoluto
    from models import Base
    from models import (
        Usuario,
        Categoria,
        Producto,
        Orden,
        DetalleOrden,
        DireccionEnvio,
        Carrito,
        MetodoPago,
        OrdenMetodoPago,
        ResenaProducto,
        HistorialPago
    )
    from database.db_connector import DBConnector


def create_staging_tables():
    """
    Crea solo las tablas STAGING (raw) en PostgreSQL usando SQL directo.
    Estas tablas almacenan datos crudos del CSV sin IDs ni foreign keys.
    
    IMPORTANTE: Usa SQL directo en lugar de SQLAlchemy ORM para evitar
    el requisito de primary keys que SQLAlchemy impone.
    
    Utiliza el DBConnector con patrón Singleton para obtener la conexión.
    """
    print("=" * 80)
    print("CREANDO TABLAS STAGING (RAW) - Usando SQL directo")
    print("=" * 80)
    
    # Obtener la instancia única del DBConnector
    db = DBConnector.get_instance()
    engine = db.get_engine()
    
    # Obtener la ruta del archivo SQL
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(current_dir, 'create_staging_tables.sql')
    
    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(
            f"No se encontró el archivo SQL: {sql_file_path}\n"
            f"El archivo debe contener las definiciones de las tablas staging."
        )
    
    try:
        # Leer el archivo SQL
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Dividir el contenido en statements individuales
        # Separar por ';' y filtrar líneas vacías y comentarios
        statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            line = line.strip()
            # Ignorar líneas vacías y comentarios completos
            if not line or line.startswith('--'):
                continue
            
            # Remover comentarios al final de la línea
            if '--' in line:
                line = line[:line.index('--')].strip()
            
            if line:
                current_statement.append(line)
                # Si la línea termina con ';', es el final del statement
                if line.endswith(';'):
                    statement = ' '.join(current_statement).rstrip(';').strip()
                    if statement:
                        statements.append(statement)
                    current_statement = []
        
        # Si queda un statement sin terminar, agregarlo
        if current_statement:
            statement = ' '.join(current_statement).strip()
            if statement:
                statements.append(statement)
        
        # Ejecutar cada statement SQL
        with engine.begin() as conn:
            for statement in statements:
                if statement:  # Asegurar que no esté vacío
                    conn.execute(text(statement))
        
        # Contar las tablas creadas (una por cada CREATE TABLE)
        tables_created = len([s for s in statements if s.upper().startswith('CREATE TABLE')])
        
        print(f"   ✓ {tables_created} tablas staging creadas/verificadas")
        print("\n" + "=" * 80)
        print(f"✓ Todas las tablas staging creadas exitosamente ({tables_created} tablas)")
        print("=" * 80)
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"✗ Error al crear las tablas staging: {str(e)}")
        print("=" * 80)
        raise


def create_production_tables():
    """
    Crea solo las tablas de PRODUCCIÓN en PostgreSQL.
    Estas tablas tienen IDs autoincrementales, foreign keys y constraints.
    
    Utiliza el DBConnector con patrón Singleton para obtener la conexión.
    """
    print("=" * 80)
    print("CREANDO TABLAS DE PRODUCCIÓN")
    print("=" * 80)
    
    # Obtener la instancia única del DBConnector
    db = DBConnector.get_instance()
    engine = db.get_engine()
    
    # Lista de modelos de producción
    production_models = [
        Categoria,      # Primero las independientes
        MetodoPago,     # Primero las independientes
        Usuario,        # Independiente
        Producto,      # Depende de Categoria
        Orden,          # Depende de Usuario
        DetalleOrden,   # Depende de Orden y Producto
        Carrito,        # Depende de Usuario y Producto
        DireccionEnvio, # Depende de Usuario
        ResenaProducto, # Depende de Usuario y Producto
        OrdenMetodoPago, # Depende de Orden y MetodoPago
        HistorialPago    # Depende de Orden y MetodoPago
    ]
    
    try:
        # Crear solo las tablas de producción
        # SQLAlchemy maneja automáticamente el orden de creación respetando dependencias
        for model in production_models:
            model.__table__.create(engine, checkfirst=True)
            print(f"   ✓ Tabla '{model.__tablename__}' creada/verificada")
        
        print("\n" + "=" * 80)
        print(f"✓ Todas las tablas de producción creadas exitosamente ({len(production_models)} tablas)")
        print("=" * 80)
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"✗ Error al crear las tablas de producción: {str(e)}")
        print("=" * 80)
        raise


def create_all_tables():
    """
    Crea todas las tablas (staging y producción) en PostgreSQL.
    Primero crea las tablas staging, luego las de producción.
    
    Utiliza el DBConnector con patrón Singleton para obtener la conexión.
    
    Nota: Esta función mantiene compatibilidad con código existente.
    """
    print("\n" + "=" * 80)
    print("CREANDO TODAS LAS TABLAS (STAGING + PRODUCCIÓN)")
    print("=" * 80)
    
    try:
        # Paso 1: Crear tablas staging
        print("\n[PASO 1/2] Creando tablas staging...")
        create_staging_tables()
        
        # Paso 2: Crear tablas de producción
        print("\n[PASO 2/2] Creando tablas de producción...")
        create_production_tables()
        
        print("\n" + "=" * 80)
        print("✓ PROCESO COMPLETADO: Todas las tablas creadas exitosamente")
        print("=" * 80)
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"✗ Error al crear las tablas: {str(e)}")
        print("=" * 80)
        raise


if __name__ == "__main__":
    # Por defecto, crear todas las tablas
    create_all_tables()