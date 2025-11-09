"""
Módulo para cargar datos desde archivos CSV a tablas existentes en PostgreSQL.
Las tablas deben estar creadas previamente usando models.py
Utiliza el comando COPY nativo de PostgreSQL vía psycopg2 para máxima eficiencia.
"""

import os
import sys
import io
import pandas as pd
import psycopg2

# Import PathManager y ETLConfig desde Utils (mismo nivel: Avance1/)
try:
    from ..Utils.path_manager import PathManager
    from ..Utils.config import ETLConfig
except ImportError:
    # Si falla el import relativo (ej: ejecutado como script), usar import absoluto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    avance1_dir = os.path.dirname(current_dir)
    utils_dir = os.path.join(avance1_dir, 'Utils')
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    from path_manager import PathManager
    from config import ETLConfig

# Configurar sys.path usando PathManager
path_manager = PathManager.get_instance()
path_manager.setup_sys_path()

# Import DBConnector desde la raíz del proyecto
from Database.db_connector import DBConnector

# Import clean_column_name desde Utils
try:
    from ..Utils.clean_column_name import clean_column_name
except ImportError:
    # Si falla el import relativo, usar import absoluto
    from clean_column_name import clean_column_name


def load_data(file_name: str, table_name: str) -> None:
    """
    Lee un archivo CSV, estandariza los nombres de columnas e inserta los datos
    en una tabla existente de PostgreSQL usando el comando COPY nativo.
    
    IMPORTANTE: Las tablas deben estar creadas previamente usando models.py
    Este módulo se usa típicamente después de ejecutar create_all_tables().
    
    Utiliza COPY de PostgreSQL vía psycopg2 para máxima eficiencia en la carga de datos.
    
    Args:
        file_name: Nombre del archivo CSV (ruta relativa desde la raíz del proyecto)
        table_name: Nombre de la tabla en PostgreSQL donde se insertarán los datos
        
    Raises:
        Exception: Si ocurre un error al leer el CSV o insertar los datos
    """
    try:
        # Obtener la ruta completa del archivo CSV usando PathManager
        csv_path = path_manager.get_csv_path(file_name)
        
        if not os.path.exists(csv_path):
            print(f"Advertencia: No se encontró el archivo {csv_path}")
            return
        
        print(f"\nLeyendo archivo: {file_name}")
        
        # Leer el CSV con pandas usando configuración centralizada
        df = pd.read_csv(csv_path, encoding=ETLConfig.CSV_ENCODING)
        
        print(f"   ✓ Archivo leído. Filas: {len(df)}, Columnas: {len(df.columns)}")
        
        # Limpiar nombres de columnas
        df.columns = [clean_column_name(col) for col in df.columns]
        print(f"   ✓ Nombres de columnas estandarizados")
        
        # Obtener la instancia única del DBConnector
        db = DBConnector.get_instance()
        
        print(f"   Cargando datos a la tabla '{table_name}' usando COPY...")
        
        # Obtener la conexión raw de psycopg2 usando el context manager del DBConnector
        with db.get_raw_connection() as conn:
            # Obtener el cursor de psycopg2
            cursor = conn.cursor()
            
            try:
                # Convertir DataFrame a CSV en memoria (StringIO)
                # Usar formato compatible con COPY CSV de PostgreSQL
                csv_buffer = io.StringIO()
                df.to_csv(
                    csv_buffer,
                    index=False,  # No incluir el índice
                    header=False,  # COPY no necesita header
                    sep=',',  # Separador de columnas
                    na_rep='',  # Representación de valores nulos (vacío para COPY)
                    quoting=1,  # QUOTE_MINIMAL (solo cuando es necesario)
                    escapechar='\\',  # Carácter de escape
                    doublequote=True,  # Escapar comillas dobles con doble comilla
                    lineterminator='\n'  # Terminador de línea Unix
                )
                csv_buffer.seek(0)  # Volver al inicio del buffer
                
                # Obtener los nombres de las columnas en el orden correcto
                columns = ', '.join(df.columns)
                
                # Ejecutar COPY FROM usando psycopg2
                # COPY es mucho más rápido que INSERT individuales
                # FORMAT CSV con DELIMITER ',' y NULL '' para valores nulos
                cursor.copy_expert(
                    f"COPY {table_name} ({columns}) FROM STDIN WITH (FORMAT CSV, DELIMITER ',', NULL '', QUOTE '\"', ESCAPE '\\')",
                    csv_buffer
                )
                
                # Confirmar la transacción
                conn.commit()
                
                print(f"   ✓ Datos cargados exitosamente a '{table_name}' ({len(df)} filas)")
                
            except Exception as e:
                # Revertir la transacción en caso de error
                conn.rollback()
                raise e
            finally:
                # Cerrar cursor (la conexión se cierra automáticamente por el context manager)
                cursor.close()
        
    except Exception as e:
        print(f"   Error al procesar {file_name}: {str(e)}")
        raise

