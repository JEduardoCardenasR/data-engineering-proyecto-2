"""
Script principal (orquestador) para el proceso ETL completo.
Crea las tablas y carga los datos desde archivos CSV a PostgreSQL.
Utiliza el DBConnector con patrón Singleton para la conexión a la base de datos.
"""

import sys

# Import PathManager desde Utils
try:
    from .Utils.path_manager import PathManager
except ImportError:
    # Si falla el import relativo (ej: ejecutado como script), usar import absoluto
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    utils_dir = os.path.join(current_dir, 'Utils')
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    from path_manager import PathManager

# Configurar sys.path usando PathManager
path_manager = PathManager.get_instance()
path_manager.setup_sys_path()

# Import funciones desde Models y ETL
try:
    from .Models.create_tables import create_all_tables
    from .ETL.load_data import load_data
except ImportError:
    # Si falla el import relativo, usar import absoluto
    from Models.create_tables import create_all_tables
    from ETL.load_data import load_data


def main():
    """
    Función principal que orquesta el proceso ETL completo:
    1. Crea todas las tablas en PostgreSQL usando los modelos ORM
    2. Carga los datos desde archivos CSV a las tablas creadas
    """
    print("\nINICIANDO PROCESO ETL COMPLETO")
    
    # Paso 1: Crear todas las tablas en PostgreSQL
    print("\nPASO 1: Creando esquema de base de datos...")
    try:
        create_all_tables()
        print("Esquema de base de datos creado exitosamente")
    except Exception as e:
        print(f"\nError al crear el esquema de base de datos: {str(e)}")
        raise
    
    # Paso 2: Cargar datos desde archivos CSV
    print("\nPASO 2: Cargando datos desde archivos CSV...")
    
    # Mapeo de archivos CSV a nombres de tablas
    tables_config = [
        {'file': '2.Usuarios.csv', 'table': 'usuarios'},
        {'file': '3.Categorias.csv', 'table': 'categorias'},
        {'file': '4.Productos.csv', 'table': 'productos'},
        {'file': '5.ordenes.csv', 'table': 'ordenes'},
        {'file': '6.detalle_ordenes.csv', 'table': 'detalle_ordenes'},
        {'file': '7.direcciones_envio.csv', 'table': 'direcciones_envio'},
        {'file': '8.carrito.csv', 'table': 'carrito'},
        {'file': '9.metodos_pago.csv', 'table': 'metodos_pago'},
        {'file': '10.ordenes_metodospago.csv', 'table': 'ordenes_metodos_pago'},
        {'file': '11.resenas_productos.csv', 'table': 'resenas_productos'},
        {'file': '12.historial_pagos.csv', 'table': 'historial_pagos'}
    ]
    
    # Cargar cada tabla
    for config in tables_config:
        try:
            load_data(
                file_name=config['file'],
                table_name=config['table']
            )
        except Exception as e:
            print(f"\nError al cargar {config['file']}: {str(e)}")
            raise
    
    # Resumen final
    print("\nPROCESO ETL COMPLETADO EXITOSAMENTE")
    print(f"\nResumen:")
    print(f"   - Tablas creadas: {len(tables_config)}")
    print(f"   - Archivos CSV procesados: {len(tables_config)}")
    print()


if __name__ == "__main__":
    main()