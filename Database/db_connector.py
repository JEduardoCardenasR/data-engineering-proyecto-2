"""
Módulo para la conexión a la base de datos PostgreSQL usando SQLAlchemy.
Implementa el patrón Singleton para asegurar una única instancia de conexión.
"""

import os
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from typing import Optional


class DBConnector:
    """
    Clase Singleton para gestionar la conexión a la base de datos PostgreSQL.
    
    Esta clase asegura que solo exista una única instancia de conexión
    durante toda la ejecución del proyecto.
    """
    
    _instance: Optional['DBConnector'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """
        Método especial que controla la creación de instancias.
        Implementa el patrón Singleton.
        """
        if cls._instance is None:
            cls._instance = super(DBConnector, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Inicializa la conexión a la base de datos.
        Solo se ejecuta una vez gracias al flag _initialized.
        """
        if not DBConnector._initialized:
            # Cargar variables de entorno desde el archivo .env
            load_dotenv()
            
            # Obtener las variables de entorno
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'avance_1_db')
            db_user = os.getenv('DB_USER', 'usuario')
            db_pass = os.getenv('DB_PASS', '')
            
            # Construir la URL de conexión de SQLAlchemy para PostgreSQL
            connection_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
            
            # Crear el Engine de SQLAlchemy
            self.engine: Engine = create_engine(
                connection_url,
                pool_pre_ping=True,  # Verifica la conexión antes de usarla
                echo=False  # Cambiar a True para ver las consultas SQL en consola
            )
            
            DBConnector._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'DBConnector':
        """
        Método de clase para obtener la instancia única del Singleton.
        
        Returns:
            DBConnector: La única instancia de la clase DBConnector.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_engine(self) -> Engine:
        """
        Retorna el Engine de SQLAlchemy creado.
        
        Returns:
            Engine: El motor de SQLAlchemy para realizar operaciones en la BD.
        """
        return self.engine
    
    @contextmanager
    def get_raw_connection(self):
        """
        Context manager para obtener una conexión raw de psycopg2.
        Útil para operaciones que requieren acceso directo a psycopg2 (ej: COPY).
        
        La conexión se cierra automáticamente al salir del contexto,
        devolviéndola al pool de conexiones.
        
        Yields:
            Connection: Conexión raw de psycopg2
            
        Example:
            ```python
            db = DBConnector.get_instance()
            with db.get_raw_connection() as conn:
                cursor = conn.cursor()
                # ... operaciones con psycopg2 ...
                conn.commit()
            ```
        """
        conn = None
        try:
            conn = self.engine.raw_connection()
            yield conn
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()  # Devuelve la conexión al pool

