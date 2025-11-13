"""
Script genérico para eliminar y recargar datos de una tabla desde su archivo CSV.

USO:
    Cambiar la variable TABLA_A_RECARGAR al inicio del script para especificar
    qué tabla se desea recargar.

    Ejemplo:
        TABLA_A_RECARGAR = 'usuarios'  # Recargará desde '2.Usuarios.csv'
        TABLA_A_RECARGAR = 'productos'  # Recargará desde '4.Productos.csv'
"""

import sys
import os

# ============================================================================
# CONFIGURACIÓN: Cambiar esta variable para recargar una tabla diferente
# ============================================================================
TABLA_A_RECARGAR = 'usuarios'  # Cambiar aquí el nombre de la tabla
# ============================================================================

# Import PathManager desde Utils
try:
    from Avance1.Utils.path_manager import PathManager
except ImportError:
    # Si falla el import relativo, usar import absoluto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    avance1_dir = os.path.join(current_dir, 'Avance1')
    utils_dir = os.path.join(avance1_dir, 'Utils')
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    from path_manager import PathManager

# Configurar sys.path usando PathManager
path_manager = PathManager.get_instance()
path_manager.setup_sys_path()

# Import funciones desde ETL y Database
try:
    from Avance1.ETL.load_data import load_data
    from Database.db_connector import DBConnector
except ImportError:
    # Si falla el import relativo, usar import absoluto
    from ETL.load_data import load_data
    from Database.db_connector import DBConnector


# Mapeo de nombres de tablas a archivos CSV
TABLA_TO_CSV = {
    'usuarios': '2.Usuarios.csv',
    'categorias': '3.Categorias.csv',
    'productos': '4.Productos.csv',
    'ordenes': '5.ordenes.csv',
    'detalle_ordenes': '6.detalle_ordenes.csv',
    'direcciones_envio': '7.direcciones_envio.csv',
    'carrito': '8.carrito.csv',
    'metodos_pago': '9.metodos_pago.csv',
    'ordenes_metodos_pago': '10.ordenes_metodospago.csv',
    'resenas_productos': '11.resenas_productos.csv',
    'historial_pagos': '12.historial_pagos.csv'
}


def truncate_table(table_name: str) -> None:
    """
    Elimina todos los registros de una tabla usando TRUNCATE.
    
    Args:
        table_name: Nombre de la tabla a truncar
        
    Raises:
        Exception: Si ocurre un error al truncar la tabla
    """
    try:
        db = DBConnector.get_instance()
        
        print(f"\nEliminando contenido de la tabla '{table_name}'...")
        
        # Obtener la conexión raw de psycopg2
        with db.get_raw_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # TRUNCATE es más eficiente que DELETE para eliminar todos los registros
                # CASCADE elimina también los registros en tablas relacionadas si hay foreign keys
                # RESTART IDENTITY reinicia las secuencias de auto-incremento
                cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
                
                # Confirmar la transacción
                conn.commit()
                
                print(f"   ✓ Contenido de la tabla '{table_name}' eliminado exitosamente")
                
            except Exception as e:
                # Revertir la transacción en caso de error
                conn.rollback()
                raise e
            finally:
                cursor.close()
                
    except Exception as e:
        print(f"   ✗ Error al eliminar contenido de la tabla '{table_name}': {str(e)}")
        raise


def reload_table_data(table_name: str) -> None:
    """
    Elimina el contenido de una tabla y recarga los datos desde su archivo CSV.
    
    Args:
        table_name: Nombre de la tabla a recargar
        
    Raises:
        ValueError: Si la tabla no está en el mapeo de tablas a CSV
        Exception: Si ocurre un error al recargar los datos
    """
    # Verificar que la tabla esté en el mapeo
    if table_name not in TABLA_TO_CSV:
        available_tables = ', '.join(TABLA_TO_CSV.keys())
        raise ValueError(
            f"La tabla '{table_name}' no está en el mapeo de tablas disponibles.\n"
            f"Tablas disponibles: {available_tables}"
        )
    
    csv_file = TABLA_TO_CSV[table_name]
    
    print("=" * 80)
    print(f"RECARGANDO DATOS DE LA TABLA: {table_name}")
    print("=" * 80)
    print(f"Archivo CSV: {csv_file}")
    print(f"Tabla destino: {table_name}")
    
    try:
        # Paso 1: Eliminar contenido de la tabla
        truncate_table(table_name)
        
        # Paso 2: Cargar datos desde CSV
        print(f"\nCargando datos desde '{csv_file}' a la tabla '{table_name}'...")
        load_data(
            file_name=csv_file,
            table_name=table_name
        )
        
        print("\n" + "=" * 80)
        print(f"✓ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        print(f"Tabla '{table_name}' recargada desde '{csv_file}'")
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"✗ ERROR AL RECARGAR LA TABLA")
        print("=" * 80)
        print(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    """
    Ejecuta el proceso de recarga de datos para la tabla especificada.
    
    Para cambiar la tabla, modificar la variable TABLA_A_RECARGAR al inicio del archivo.
    """
    try:
        reload_table_data(TABLA_A_RECARGAR)
    except Exception as e:
        print(f"\nError fatal: {str(e)}")
        sys.exit(1)

