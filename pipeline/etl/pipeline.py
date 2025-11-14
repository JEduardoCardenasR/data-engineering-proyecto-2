"""
Módulo de pipeline ETL modular.
Permite ejecutar el proceso ETL completo o por pasos individuales.

Funciones disponibles:
- run_full_pipeline(): Ejecuta todo el proceso ETL
- run_staging_load(): Solo carga datos crudos a staging
- run_transformations(): Solo aplica transformaciones sobre staging
- run_production_load(): Solo carga datos transformados a producción

Útil para desarrollo, debugging y mantenimiento incremental.
"""

import sys
import pandas as pd
from sqlalchemy import text
from typing import Dict, Optional

# Import PathManager desde utils
try:
    from ..utils.path_manager import PathManager
except ImportError:
    import os
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
    from ..models.create_tables import create_staging_tables, create_production_tables
    from .load_raw_data import load_raw_data
    from .transformations import apply_transformations
    from .load_to_production import load_all_to_production
    from database.db_connector import DBConnector
except ImportError:
    # Si falla el import relativo, usar import absoluto
    from pipeline.models.create_tables import create_staging_tables, create_production_tables
    from pipeline.etl.load_raw_data import load_raw_data
    from pipeline.etl.transformations import apply_transformations
    from pipeline.etl.load_to_production import load_all_to_production
    from database.db_connector import DBConnector


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Mapeo de archivos CSV a nombres de tablas staging
TABLES_CONFIG = [
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


# ============================================================================
# FUNCIONES DE PIPELINE POR PASOS
# ============================================================================

def run_staging_load(create_tables: bool = True) -> None:
    """
    Ejecuta solo la carga de datos crudos a staging.
    
    Pasos ejecutados:
    1. Crear tablas staging (opcional)
    2. Cargar datos desde CSV a tablas staging
    
    Args:
        create_tables: Si True, crea las tablas staging antes de cargar.
                      Si False, asume que las tablas ya existen.
    """
    print("\n" + "="*80)
    print("EJECUTANDO: Carga a STAGING")
    print("="*80)
    
    db = DBConnector.get_instance()
    engine = db.get_engine()
    
    try:
        # Paso 1: Crear tablas staging (si se solicita)
        if create_tables:
            print("\n[1/2] Creando tablas STAGING...")
            create_staging_tables()
        else:
            print("\n[1/2] Saltando creación de tablas (asumiendo que ya existen)")
        
        # Paso 2: Cargar datos crudos a staging
        print("\n[2/2] Cargando datos crudos a STAGING...")
        for config in TABLES_CONFIG:
            try:
                load_raw_data(
                    file_name=config['file'],
                    table_name_raw=config['table_raw']
                )
            except Exception as e:
                print(f"\n✗ Error al cargar {config['file']} a staging: {str(e)}")
                raise
        
        print("\n" + "="*80)
        print("✓ CARGA A STAGING COMPLETADA")
        print("="*80)
        print(f"   - Archivos CSV procesados: {len(TABLES_CONFIG)}")
        print()
        
    except Exception as e:
        print("\n" + "="*80)
        print("✗ ERROR EN CARGA A STAGING")
        print("="*80)
        print(f"Error: {str(e)}")
        print()
        raise


def run_transformations() -> Dict[str, pd.DataFrame]:
    """
    Ejecuta solo las transformaciones sobre datos en staging.
    
    Pasos ejecutados:
    1. Leer datos de staging
    2. Aplicar transformaciones
    3. Actualizar staging con datos transformados
    
    Returns:
        Diccionario con DataFrames transformados: {table_raw: DataFrame}
    """
    print("\n" + "="*80)
    print("EJECUTANDO: Transformaciones sobre STAGING")
    print("="*80)
    
    db = DBConnector.get_instance()
    engine = db.get_engine()
    
    staging_data = {}
    
    try:
        # Leer datos de staging para transformar
        for config in TABLES_CONFIG:
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
        
        print("\n" + "="*80)
        print("✓ TRANSFORMACIONES COMPLETADAS")
        print("="*80)
        print(f"   - Tablas transformadas: {len(staging_data)}")
        print()
        
        return staging_data
        
    except Exception as e:
        print("\n" + "="*80)
        print("✗ ERROR EN TRANSFORMACIONES")
        print("="*80)
        print(f"Error: {str(e)}")
        print()
        raise


def run_production_load(create_tables: bool = True) -> Dict[str, Dict]:
    """
    Ejecuta solo la carga de datos transformados a producción.
    
    Pasos ejecutados:
    1. Crear tablas de producción (opcional)
    2. Cargar datos desde staging a producción
    3. Resolver foreign keys (automático)
    
    Args:
        create_tables: Si True, crea las tablas de producción antes de cargar.
                      Si False, asume que las tablas ya existen.
    
    Returns:
        Diccionario con mapeos de IDs por tabla
    """
    print("\n" + "="*80)
    print("EJECUTANDO: Carga a PRODUCCIÓN")
    print("="*80)
    print("(Las foreign keys se resuelven automáticamente durante la carga)")
    
    try:
        # Paso 1: Crear tablas de producción (si se solicita)
        if create_tables:
            print("\n[1/2] Creando tablas de PRODUCCIÓN...")
            create_production_tables()
        else:
            print("\n[1/2] Saltando creación de tablas (asumiendo que ya existen)")
        
        # Paso 2: Cargar datos transformados a producción y resolver FKs
        print("\n[2/2] Cargando datos a PRODUCCIÓN y resolviendo Foreign Keys...")
        id_mappings = load_all_to_production()
        
        # Importar LOAD_ORDER para contar tablas cargadas
        try:
            from pipeline.etl.load_to_production import LOAD_ORDER
        except ImportError:
            from .load_to_production import LOAD_ORDER
        
        print("\n" + "="*80)
        print("✓ CARGA A PRODUCCIÓN COMPLETADA")
        print("="*80)
        print(f"   - Tablas cargadas: {len(LOAD_ORDER)}")
        print(f"   - Mapeos de IDs creados: {len(id_mappings)}")
        print(f"   - Foreign keys resueltas: Automático")
        print()
        
        return id_mappings
        
    except Exception as e:
        print("\n" + "="*80)
        print("✗ ERROR EN CARGA A PRODUCCIÓN")
        print("="*80)
        print(f"Error: {str(e)}")
        print()
        raise


def run_full_pipeline() -> Dict[str, Dict]:
    """
    Ejecuta el proceso ETL completo de principio a fin.
    
    Pasos ejecutados:
    1. Crear tablas staging
    2. Cargar datos crudos a staging
    3. Crear tablas de producción
    4. Ejecutar transformaciones sobre staging
    5. Cargar datos transformados a producción (con generación de IDs)
    6. Resolver foreign keys (automático)
    
    Returns:
        Diccionario con mapeos de IDs por tabla
    
    Nota: Esta función es equivalente a ejecutar main.py
    """
    print("\n" + "="*80)
    print("EJECUTANDO: Pipeline ETL COMPLETO")
    print("(STAGING → TRANSFORMACIÓN → PRODUCCIÓN)")
    print("="*80)
    
    try:
        # Paso 1: Crear tablas staging
        print("\n[PASO 1/6] Creando tablas STAGING")
        print("="*80)
        create_staging_tables()
        
        # Paso 2: Cargar datos crudos a staging
        print("\n[PASO 2/6] Cargando datos crudos a STAGING")
        print("="*80)
        for config in TABLES_CONFIG:
            try:
                load_raw_data(
                    file_name=config['file'],
                    table_name_raw=config['table_raw']
                )
            except Exception as e:
                print(f"\n✗ Error al cargar {config['file']} a staging: {str(e)}")
                raise
        
        # Paso 3: Crear tablas de producción
        print("\n[PASO 3/6] Creando tablas de PRODUCCIÓN")
        print("="*80)
        create_production_tables()
        
        # Paso 4: Ejecutar transformaciones sobre staging
        print("\n[PASO 4/6] Aplicando TRANSFORMACIONES sobre staging")
        print("="*80)
        staging_data = run_transformations()
        
        # Paso 5-6: Cargar datos transformados a producción y resolver FKs
        print("\n[PASO 5-6/6] Cargando datos a PRODUCCIÓN y resolviendo Foreign Keys")
        print("="*80)
        id_mappings = run_production_load(create_tables=False)  # Ya creadas en paso 3
        
        # Importar LOAD_ORDER para contar tablas cargadas
        try:
            from pipeline.etl.load_to_production import LOAD_ORDER
        except ImportError:
            from .load_to_production import LOAD_ORDER
        
        # Resumen final
        print("\n" + "="*80)
        print("✓ PROCESO ETL COMPLETO FINALIZADO")
        print("="*80)
        print(f"\nResumen:")
        print(f"   - Tablas staging creadas: {len(TABLES_CONFIG)}")
        print(f"   - Archivos CSV procesados: {len(TABLES_CONFIG)}")
        print(f"   - Tablas de producción creadas: {len(TABLES_CONFIG)}")
        print(f"   - Transformaciones aplicadas: {len(staging_data)}")
        print(f"   - Tablas cargadas a producción: {len(LOAD_ORDER)}")
        print(f"   - Mapeos de IDs creados: {len(id_mappings)}")
        print(f"   - Foreign keys resueltas: Automático")
        print()
        
        return id_mappings
        
    except Exception as e:
        print("\n" + "="*80)
        print("✗ ERROR EN EL PROCESO ETL COMPLETO")
        print("="*80)
        print(f"Error: {str(e)}")
        print()
        raise

