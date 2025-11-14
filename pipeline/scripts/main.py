"""
Script principal (orquestador) para el proceso ETL completo.
Implementa el flujo: Extract → Transform → Load (ETL) con staging.

Flujo completo:
1. Crear tablas staging
2. Cargar datos crudos a staging
3. Crear tablas de producción
4. Ejecutar transformaciones sobre staging
5. Cargar datos transformados a producción (con generación de IDs)
6. Resolver foreign keys (automático en load_all_to_production)

Utiliza el DBConnector con patrón Singleton para la conexión a la base de datos.
"""

import sys
import os
import pandas as pd
from sqlalchemy import text

# Agregar la raíz del proyecto al sys.path si se ejecuta como script
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))  # Sube dos niveles: scripts -> pipeline -> raíz
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# Import PathManager desde utils
try:
    from pipeline.utils.path_manager import PathManager
except ImportError:
    # Si falla, intentar import relativo
    try:
        from ..utils.path_manager import PathManager
    except ImportError:
        # Último recurso: agregar utils al path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pipeline_dir = os.path.dirname(current_dir)
        utils_dir = os.path.join(pipeline_dir, 'utils')
        if utils_dir not in sys.path:
            sys.path.insert(0, utils_dir)
        from path_manager import PathManager

# Configurar sys.path usando PathManager
path_manager = PathManager.get_instance()
path_manager.setup_sys_path()

# Import funciones desde models y etl
try:
    from pipeline.models.create_tables import create_staging_tables, create_production_tables
    from pipeline.etl.load_raw_data import load_raw_data
    from pipeline.etl.transformations import apply_transformations
    from pipeline.etl.load_to_production import load_all_to_production
    from database.db_connector import DBConnector
except ImportError:
    # Si falla el import absoluto, intentar relativo
    try:
        from ..models.create_tables import create_staging_tables, create_production_tables
        from ..etl.load_raw_data import load_raw_data
        from ..etl.transformations import apply_transformations
        from ..etl.load_to_production import load_all_to_production
        from database.db_connector import DBConnector
    except ImportError:
        # Último recurso: imports directos
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pipeline_dir = os.path.dirname(current_dir)
        if pipeline_dir not in sys.path:
            sys.path.insert(0, pipeline_dir)
        from models.create_tables import create_staging_tables, create_production_tables
        from etl.load_raw_data import load_raw_data
        from etl.transformations import apply_transformations
        from etl.load_to_production import load_all_to_production
        from database.db_connector import DBConnector


def main():
    """
    Función principal que orquesta el proceso ETL completo con staging:
    1. Crear tablas staging
    2. Cargar datos crudos a staging
    3. Crear tablas de producción
    4. Ejecutar transformaciones sobre staging
    5. Cargar datos transformados a producción (con generación de IDs)
    6. Resolver foreign keys (automático)
    """
    print("\n" + "="*80)
    print("INICIANDO PROCESO ETL COMPLETO (STAGING → TRANSFORMACIÓN → PRODUCCIÓN)")
    print("="*80)
    
    # Mapeo de archivos CSV a nombres de tablas staging
    tables_config = [
        {'file': '2.Usuarios.csv', 'table_raw': 'usuarios_raw'},
        {'file': '3.Categorias.csv', 'table_raw': 'categorias_raw'},
        {'file': '4.Productos.csv', 'table_raw': 'productos_raw'},
        {'file': '5.ordenes.csv', 'table_raw': 'ordenes_raw'},
        {'file': '6.detalle_ordenes.csv', 'table_raw': 'detalle_ordenes_raw'},
        {'file': '7.direcciones_envio.csv', 'table_raw': 'direcciones_envio_raw'},
        {'file': '8.carrito.csv', 'table_raw': 'carrito_raw'},
        {'file': '9.metodos_pago.csv', 'table_raw': 'metodos_pago_raw'},
        {'file': '10.ordenes_metodospago.csv', 'table_raw': 'ordenes_metodos_pago_raw'},
        {'file': '11.resenas_productos.csv', 'table_raw': 'resenas_productos_raw'},
        {'file': '12.historial_pagos.csv', 'table_raw': 'historial_pagos_raw'}
    ]
    
    db = DBConnector.get_instance()
    engine = db.get_engine()
    
    try:
        # ========================================================================
        # PASO 1: Crear tablas staging
        # ========================================================================
        print("\n" + "="*80)
        print("PASO 1/6: Creando tablas STAGING")
        print("="*80)
        create_staging_tables()
        
        # ========================================================================
        # PASO 2: Cargar datos crudos a staging
        # ========================================================================
        print("\n" + "="*80)
        print("PASO 2/6: Cargando datos crudos a STAGING")
        print("="*80)
        for config in tables_config:
            try:
                load_raw_data(
                    file_name=config['file'],
                    table_name_raw=config['table_raw']
                )
            except Exception as e:
                print(f"\n✗ Error al cargar {config['file']} a staging: {str(e)}")
                raise
        
        # ========================================================================
        # PASO 3: Crear tablas de producción
        # ========================================================================
        print("\n" + "="*80)
        print("PASO 3/6: Creando tablas de PRODUCCIÓN")
        print("="*80)
        create_production_tables()
        
        # ========================================================================
        # PASO 4: Ejecutar transformaciones sobre staging
        # ========================================================================
        print("\n" + "="*80)
        print("PASO 4/6: Aplicando TRANSFORMACIONES sobre staging")
        print("="*80)
        
        # Leer datos de staging para transformar
        staging_data = {}
        for config in tables_config:
            table_raw = config['table_raw']
            print(f"\n   Transformando: {table_raw}")
            try:
                # Leer datos de staging
                query = f"SELECT * FROM {table_raw}"
                df = pd.read_sql(query, engine)
                
                if len(df) == 0:
                    print(f"      ⚠ Tabla {table_raw} está vacía, saltando transformación")
                    continue
                
                # Aplicar transformaciones
                # Para ordenes_raw, necesitamos detalle_ordenes_raw
                if table_raw == 'ordenes_raw':
                    query_detalle = "SELECT * FROM detalle_ordenes_raw"
                    df_detalle = pd.read_sql(query_detalle, engine)
                    df_transformed = apply_transformations(
                        table_raw,
                        df,
                        df_detalle_ordenes=df_detalle
                    )
                else:
                    df_transformed = apply_transformations(table_raw, df)
                
                # Actualizar staging con datos transformados
                # Eliminar datos antiguos y reinsertar transformados
                with engine.begin() as conn:
                    conn.execute(text(f"TRUNCATE TABLE {table_raw} CASCADE"))
                
                # Insertar datos transformados
                df_transformed.to_sql(
                    table_raw,
                    engine,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
                
                print(f"      ✓ {len(df_transformed)} filas transformadas y actualizadas en {table_raw}")
                staging_data[table_raw] = df_transformed
                
            except Exception as e:
                print(f"      ✗ Error al transformar {table_raw}: {str(e)}")
                raise
        
        # ========================================================================
        # PASO 5 y 6: Cargar datos transformados a producción y resolver FKs
        # ========================================================================
        print("\n" + "="*80)
        print("PASO 5-6/6: Cargando datos a PRODUCCIÓN y resolviendo Foreign Keys")
        print("="*80)
        print("(Las foreign keys se resuelven automáticamente durante la carga)")
        
        id_mappings = load_all_to_production()
        
        # Importar LOAD_ORDER para contar tablas cargadas
        from pipeline.etl.load_to_production import LOAD_ORDER
        
        # ========================================================================
        # RESUMEN FINAL
        # ========================================================================
        print("\n" + "="*80)
        print("✓ PROCESO ETL COMPLETADO EXITOSAMENTE")
        print("="*80)
        print(f"\nResumen:")
        print(f"   - Tablas staging creadas: {len(tables_config)}")
        print(f"   - Archivos CSV procesados: {len(tables_config)}")
        print(f"   - Tablas de producción creadas: {len(tables_config)}")
        print(f"   - Transformaciones aplicadas: {len(tables_config)}")
        print(f"   - Tablas cargadas a producción: {len(LOAD_ORDER)}")
        print(f"   - Mapeos de IDs creados: {len(id_mappings)}")
        print(f"   - Foreign keys resueltas: Automático")
        print()
        
    except Exception as e:
        print("\n" + "="*80)
        print("✗ ERROR EN EL PROCESO ETL")
        print("="*80)
        print(f"Error: {str(e)}")
        print()
        raise


if __name__ == "__main__":
    main()