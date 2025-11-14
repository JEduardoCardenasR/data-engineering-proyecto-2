"""
Módulo para cargar datos crudos desde archivos CSV a tablas STAGING en PostgreSQL.
Las tablas staging deben estar creadas previamente usando create_staging_tables() (SQL directo).

IMPORTANTE: Esta función carga datos CRUDOS (raw) a tablas staging usando SOLO SQL.
- No usa ORM (SQLAlchemy) para staging
- Lee las columnas directamente desde PostgreSQL usando SQL
- Excluye columnas de ID primario si existen en el CSV
- Mantiene columnas de foreign keys como referencias numéricas crudas
- No aplica constraints ni validaciones (eso se hace en producción)

Utiliza el comando COPY nativo de PostgreSQL vía psycopg2 para máxima eficiencia.
"""

import os
import sys
import io
import pandas as pd
import psycopg2
from typing import List, Optional

# Import PathManager y ETLConfig desde utils (mismo nivel: pipeline/)
try:
    from ..utils.path_manager import PathManager
    from ..utils.config import ETLConfig
except ImportError:
    # Si falla el import relativo (ej: ejecutado como script), usar import absoluto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline_dir = os.path.dirname(current_dir)
    utils_dir = os.path.join(pipeline_dir, 'utils')
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    from path_manager import PathManager
    from config import ETLConfig

# Configurar sys.path usando PathManager
path_manager = PathManager.get_instance()
path_manager.setup_sys_path()

# Import DBConnector desde la raíz del proyecto
from database.db_connector import DBConnector

# Import clean_column_name desde utils
try:
    from ..utils.clean_column_name import clean_column_name
except ImportError:
    # Si falla el import relativo, usar import absoluto
    from clean_column_name import clean_column_name

# Lista de columnas de ID primario que deben excluirse del CSV
PRIMARY_KEY_COLUMNS = {
    'usuario_id',
    'categoria_id',
    'producto_id',
    'orden_id',
    'detalle_id',
    'direccion_id',
    'carrito_id',
    'metodo_pago_id',
    'orden_metodo_id',
    'resena_id',
    'pago_id'
}


def get_expected_columns(table_name_raw: str) -> List[str]:
    """
    Obtiene las columnas esperadas para una tabla staging leyendo directamente desde PostgreSQL.
    Usa SQL puro, sin depender de modelos ORM.
    
    Args:
        table_name_raw: Nombre de la tabla staging (ej: 'usuarios_raw')
        
    Returns:
        Lista de nombres de columnas esperadas (sin IDs primarios)
        
    Raises:
        ValueError: Si la tabla no existe o no se pueden leer las columnas
    """
    db = DBConnector.get_instance()
    
    try:
        # Consulta SQL para obtener las columnas de la tabla
        # Excluimos columnas que sean primary keys (aunque en staging no deberían existir)
        query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
        """
        
        with db.get_raw_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (table_name_raw,))
            columns = [row[0] for row in cursor.fetchall()]
            cursor.close()
        
        if not columns:
            raise ValueError(
                f"La tabla '{table_name_raw}' no existe o no tiene columnas.\n"
                f"Asegúrate de haber ejecutado create_staging_tables() primero."
            )
        
        return columns
        
    except Exception as e:
        raise ValueError(
            f"Error al leer columnas de la tabla '{table_name_raw}': {str(e)}\n"
            f"Asegúrate de que la tabla existe y está creada correctamente."
        )


def filter_columns_for_staging(df: pd.DataFrame, table_name_raw: str) -> pd.DataFrame:
    """
    Filtra las columnas del DataFrame para que coincidan con las esperadas en staging.
    Excluye columnas de ID primario si existen en el CSV.
    
    Args:
        df: DataFrame con datos del CSV
        table_name_raw: Nombre de la tabla staging destino
        
    Returns:
        DataFrame filtrado con solo las columnas esperadas en staging
    """
    # Obtener columnas esperadas en la tabla staging
    expected_columns = get_expected_columns(table_name_raw)
    
    # Obtener columnas disponibles en el DataFrame
    available_columns = set(df.columns)
    
    # Filtrar: solo mantener columnas que están en expected_columns
    # y que existen en el DataFrame
    columns_to_keep = [col for col in expected_columns if col in available_columns]
    
    # Verificar que tenemos al menos algunas columnas
    if not columns_to_keep:
        raise ValueError(
            f"No se encontraron columnas válidas para la tabla '{table_name_raw}'.\n"
            f"Columnas esperadas: {expected_columns}\n"
            f"Columnas disponibles en CSV: {list(available_columns)}"
        )
    
    # Crear DataFrame filtrado
    df_filtered = df[columns_to_keep].copy()
    
    # Informar sobre columnas excluidas
    excluded_columns = available_columns - set(columns_to_keep)
    if excluded_columns:
        print(f"   ⚠ Columnas excluidas (no esperadas en staging): {sorted(excluded_columns)}")
    
    return df_filtered


def load_raw_data(file_name: str, table_name_raw: str) -> None:
    """
    Lee un archivo CSV, filtra columnas (excluyendo IDs primarios) e inserta los datos
    en una tabla STAGING de PostgreSQL usando el comando COPY nativo.
    
    IMPORTANTE: 
    - Las tablas staging deben estar creadas previamente usando create_staging_tables()
    - Esta función carga datos CRUDOS sin validaciones ni constraints
    - Excluye automáticamente columnas de ID primario si existen en el CSV
    - Mantiene columnas de foreign keys como referencias numéricas crudas
    
    Utiliza COPY de PostgreSQL vía psycopg2 para máxima eficiencia en la carga de datos.
    
    Args:
        file_name: Nombre del archivo CSV (ruta relativa desde la raíz del proyecto)
        table_name_raw: Nombre de la tabla STAGING en PostgreSQL (debe terminar en '_raw')
                      Ejemplo: 'usuarios_raw', 'productos_raw'
        
    Raises:
        ValueError: Si la tabla no está en el mapeo o no hay columnas válidas
        Exception: Si ocurre un error al leer el CSV o insertar los datos
    """
    try:
        # Validar que el nombre de tabla termine en '_raw'
        if not table_name_raw.endswith('_raw'):
            raise ValueError(
                f"El nombre de tabla debe terminar en '_raw'.\n"
                f"Recibido: '{table_name_raw}'\n"
                f"Ejemplo correcto: 'usuarios_raw'"
            )
        
        # Obtener la ruta completa del archivo CSV usando PathManager
        csv_path = path_manager.get_csv_path(file_name)
        
        if not os.path.exists(csv_path):
            print(f"Advertencia: No se encontró el archivo {csv_path}")
            return
        
        print(f"\n{'='*80}")
        print(f"CARGANDO DATOS CRUDOS A STAGING: {table_name_raw}")
        print(f"{'='*80}")
        print(f"Archivo CSV: {file_name}")
        
        # Leer el CSV con pandas usando configuración centralizada
        df = pd.read_csv(csv_path, encoding=ETLConfig.CSV_ENCODING)
        
        print(f"   ✓ Archivo leído. Filas: {len(df)}, Columnas originales: {len(df.columns)}")
        
        # Limpiar nombres de columnas (camelCase a snake_case)
        df.columns = [clean_column_name(col) for col in df.columns]
        print(f"   ✓ Nombres de columnas estandarizados")
        
        # Filtrar columnas para staging (excluir IDs primarios, mantener solo las esperadas)
        df_filtered = filter_columns_for_staging(df, table_name_raw)
        print(f"   ✓ Columnas filtradas. Columnas a cargar: {len(df_filtered.columns)}")
        print(f"   ✓ Columnas: {', '.join(df_filtered.columns)}")
        
        # Obtener la instancia única del DBConnector
        db = DBConnector.get_instance()
        
        print(f"\n   Cargando datos a la tabla '{table_name_raw}' usando COPY...")
        
        # Obtener la conexión raw de psycopg2 usando el context manager del DBConnector
        with db.get_raw_connection() as conn:
            # Obtener el cursor de psycopg2
            cursor = conn.cursor()
            
            try:
                # Convertir DataFrame filtrado a CSV en memoria (StringIO)
                # Usar formato compatible con COPY CSV de PostgreSQL
                csv_buffer = io.StringIO()
                df_filtered.to_csv(
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
                columns = ', '.join(df_filtered.columns)
                
                # Ejecutar COPY FROM usando psycopg2
                # COPY es mucho más rápido que INSERT individuales
                # FORMAT CSV con DELIMITER ',' y NULL '' para valores nulos
                cursor.copy_expert(
                    f"COPY {table_name_raw} ({columns}) FROM STDIN WITH (FORMAT CSV, DELIMITER ',', NULL '', QUOTE '\"', ESCAPE '\\')",
                    csv_buffer
                )
                
                # Confirmar la transacción
                conn.commit()
                
                print(f"   ✓ Datos cargados exitosamente a '{table_name_raw}' ({len(df_filtered)} filas)")
                print(f"{'='*80}\n")
                
            except Exception as e:
                # Revertir la transacción en caso de error
                conn.rollback()
                raise e
            finally:
                # Cerrar cursor (la conexión se cierra automáticamente por el context manager)
                cursor.close()
        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"✗ ERROR al procesar {file_name}: {str(e)}")
        print(f"{'='*80}\n")
        raise

