"""
Módulo para cargar datos desde tablas STAGING a tablas de PRODUCCIÓN.
Maneja generación automática de IDs y resolución de foreign keys.

IMPORTANTE: 
- Las tablas de producción deben estar creadas previamente
- Los datos en staging deben estar transformados y validados
- Se respeta el orden de carga (tablas independientes primero)
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import text

# Import PathManager desde utils
try:
    from ..utils.path_manager import PathManager
except ImportError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline_dir = os.path.dirname(current_dir)
    utils_dir = os.path.join(pipeline_dir, 'utils')
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    from path_manager import PathManager

# Configurar sys.path usando PathManager
path_manager = PathManager.get_instance()
path_manager.setup_sys_path()

# Import DBConnector desde la raíz del proyecto
from database.db_connector import DBConnector


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def _get_primary_key_column(table_name: str, engine) -> Optional[str]:
    """
    Obtiene el nombre real de la columna primary key de una tabla usando SQL.
    
    Args:
        table_name: Nombre de la tabla
        engine: SQLAlchemy engine
        
    Returns:
        Nombre de la columna primary key, o None si no se encuentra
    """
    query = """
        SELECT ku.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage ku
            ON tc.constraint_name = ku.constraint_name
            AND tc.table_schema = ku.table_schema
        WHERE tc.table_name = :table_name
            AND tc.table_schema = 'public'
            AND tc.constraint_type = 'PRIMARY KEY'
        LIMIT 1;
    """
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), {'table_name': table_name})
            row = result.fetchone()
            if row:
                return row[0]
    except Exception as e:
        print(f"   ⚠ Error al obtener primary key de '{table_name}': {str(e)}")
    
    # Fallback: intentar patrones comunes
    # Remover 's' final si existe (categorias -> categoria_id)
    if table_name.endswith('s'):
        fallback = f"{table_name[:-1]}_id"
    elif '_' in table_name:
        fallback = f"{table_name.split('_')[0]}_id"
    else:
        fallback = f"{table_name}_id"
    
    return fallback


# ============================================================================
# CONFIGURACIÓN DE ORDEN Y MAPEO DE TABLAS
# ============================================================================

# Orden de carga: primero independientes, luego dependientes
LOAD_ORDER = [
    # Nivel 1: Tablas independientes (sin foreign keys)
    ('categorias_raw', 'categorias', ['nombre']),  # Usar nombre como identificador natural
    ('metodos_pago_raw', 'metodos_pago', ['nombre']),  # Usar nombre como identificador natural
    ('usuarios_raw', 'usuarios', ['dni', 'email']),  # Usar dni o email como identificador natural
    
    # Nivel 2: Dependen de nivel 1
    ('productos_raw', 'productos', ['nombre'], {'categoria_id': 'categorias'}),  # FK a categorias
    ('ordenes_raw', 'ordenes', None, {'usuario_id': 'usuarios'}),  # FK a usuarios
    
    # Nivel 3: Dependen de nivel 2
    ('detalle_ordenes_raw', 'detalle_ordenes', None, {
        'orden_id': 'ordenes',
        'producto_id': 'productos'
    }),
    ('carrito_raw', 'carrito', None, {
        'usuario_id': 'usuarios',
        'producto_id': 'productos'
    }),
    ('direcciones_envio_raw', 'direcciones_envio', None, {
        'usuario_id': 'usuarios'
    }),
    ('resenas_productos_raw', 'resenas_productos', None, {
        'usuario_id': 'usuarios',
        'producto_id': 'productos'
    }),
    ('ordenes_metodos_pago_raw', 'ordenes_metodos_pago', None, {
        'orden_id': 'ordenes',
        'metodo_pago_id': 'metodos_pago'
    }),
    ('historial_pagos_raw', 'historial_pagos', None, {
        'orden_id': 'ordenes',
        'metodo_pago_id': 'metodos_pago'
    })
]

# Mapeo de tablas staging a producción
STAGING_TO_PRODUCTION = {
    'usuarios_raw': 'usuarios',
    'categorias_raw': 'categorias',
    'productos_raw': 'productos',
    'ordenes_raw': 'ordenes',
    'detalle_ordenes_raw': 'detalle_ordenes',
    'direcciones_envio_raw': 'direcciones_envio',
    'carrito_raw': 'carrito',
    'metodos_pago_raw': 'metodos_pago',
    'ordenes_metodos_pago_raw': 'ordenes_metodos_pago',
    'resenas_productos_raw': 'resenas_productos',
    'historial_pagos_raw': 'historial_pagos'
}


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def create_id_mapping(
    engine,
    source_table: str,
    target_table: str,
    natural_keys: List[str],
    source_id_column: Optional[str] = None
) -> Dict[Any, int]:
    """
    Crea un mapeo de IDs de staging a IDs de producción usando identificadores naturales.
    
    Args:
        engine: SQLAlchemy engine
        source_table: Nombre de la tabla staging
        target_table: Nombre de la tabla de producción
        natural_keys: Lista de columnas que forman el identificador natural
        source_id_column: Columna de ID en staging (opcional, para tablas con IDs en staging)
        
    Returns:
        Diccionario mapeando valores de identificador natural -> ID de producción
    """
    mapping = {}
    
    try:
        # Leer datos de staging
        query_source = f"SELECT * FROM {source_table}"
        df_source = pd.read_sql(query_source, engine)
        
        if len(df_source) == 0:
            return mapping
        
        # Leer datos de producción (ya cargados)
        query_target = f"SELECT * FROM {target_table}"
        df_target = pd.read_sql(query_target, engine)
        
        if len(df_target) == 0:
            return mapping
        
        # Obtener el nombre real de la columna primary key desde PostgreSQL
        target_id_column = _get_primary_key_column(target_table, engine)
        if not target_id_column or target_id_column not in df_target.columns:
            # Intentar otros patrones comunes
            if 'id' in df_target.columns:
                target_id_column = 'id'
            else:
                # Buscar columna que termine en _id
                id_columns = [col for col in df_target.columns if col.endswith('_id')]
                if id_columns:
                    target_id_column = id_columns[0]
                else:
                    return mapping
        
        # Crear mapeo usando identificadores naturales
        if natural_keys and all(key in df_source.columns for key in natural_keys):
            # Crear clave compuesta en source
            if len(natural_keys) == 1:
                df_source['_natural_key'] = df_source[natural_keys[0]].astype(str)
            else:
                df_source['_natural_key'] = df_source[natural_keys].apply(
                    lambda row: '|'.join(row.astype(str)), axis=1
                )
            
            # Crear clave compuesta en target
            if len(natural_keys) == 1:
                df_target['_natural_key'] = df_target[natural_keys[0]].astype(str)
            else:
                df_target['_natural_key'] = df_target[natural_keys].apply(
                    lambda row: '|'.join(row.astype(str)), axis=1
                )
            
            # Hacer merge para obtener mapeo
            merged = df_source.merge(
                df_target[[target_id_column, '_natural_key']],
                on='_natural_key',
                how='left'
            )
            
            # Crear diccionario de mapeo
            if source_id_column and source_id_column in df_source.columns:
                # Si hay ID en staging, mapear staging_id -> production_id
                for _, row in merged.iterrows():
                    if pd.notna(row[target_id_column]):
                        mapping[row[source_id_column]] = int(row[target_id_column])
            else:
                # Si no hay ID en staging, usar índice o posición
                for idx, row in merged.iterrows():
                    if pd.notna(row[target_id_column]):
                        mapping[idx] = int(row[target_id_column])
        
    except Exception as e:
        print(f"   ⚠ Error al crear mapeo de IDs: {str(e)}")
    
    return mapping


def resolve_foreign_keys(
    df: pd.DataFrame,
    fk_mappings: Dict[str, str],
    id_mappings: Dict[str, Dict[Any, int]],
    engine,
    staging_data: Optional[Dict[str, pd.DataFrame]] = None
) -> pd.DataFrame:
    """
    Resuelve foreign keys en un DataFrame usando mapeos de IDs.
    
    Estrategia:
    1. Si el valor en staging es un ID numérico que existe en el mapeo, mapearlo directamente
    2. Si no, intentar usar el orden de inserción (asumiendo que staging y production tienen el mismo orden)
    3. Si hay datos de staging disponibles, usar identificadores naturales para mapear
    
    Args:
        df: DataFrame con foreign keys a resolver
        fk_mappings: Diccionario {fk_column: target_table}
        id_mappings: Diccionario {table_name: {natural_key: production_id}} o {table_name: {staging_id: production_id}}
        engine: SQLAlchemy engine
        staging_data: Diccionario opcional con datos de staging para mapeo por identificadores naturales
        
    Returns:
        DataFrame con foreign keys resueltas
    """
    df_resolved = df.copy()
    
    for fk_column, target_table in fk_mappings.items():
        if fk_column not in df_resolved.columns:
            continue
        
        if target_table not in id_mappings:
            print(f"      ⚠ No hay mapeo disponible para {target_table}, manteniendo valores originales")
            continue
        
        mapping = id_mappings[target_table]
        
        # Leer datos de staging de la tabla target para mapeo por posición
        try:
            source_table_name = f"{target_table}_raw"
            if staging_data and source_table_name in staging_data:
                df_staging_target = staging_data[source_table_name]
            else:
                query_staging = f"SELECT * FROM {source_table_name}"
                df_staging_target = pd.read_sql(query_staging, engine)
            
            # Obtener nombre real de la columna primary key
            target_id_col = _get_primary_key_column(target_table, engine)
            if not target_id_col:
                target_id_col = f"{target_table.split('_')[0]}_id"  # Fallback
            
            # Leer datos de producción de la tabla target
            query_production = f"SELECT * FROM {target_table} ORDER BY {target_id_col}"
            df_production_target = pd.read_sql(query_production, engine)
            
            # Crear mapeo por posición (asumiendo mismo orden)
            position_mapping = {}
            if len(df_staging_target) == len(df_production_target):
                if target_id_col in df_production_target.columns:
                    for idx, staging_row in df_staging_target.iterrows():
                        if idx < len(df_production_target):
                            # Usar el índice de staging como clave
                            position_mapping[idx] = int(df_production_target.iloc[idx][target_id_col])
            
            # Resolver foreign keys
            def map_fk(value, original_idx):
                if pd.isna(value):
                    return None
                
                # Intentar mapeo directo (si el valor es una clave en el mapeo)
                # Esto funciona para natural keys (strings) o índices (ints)
                if value in mapping:
                    return mapping[value]
                
                # Si el mapeo usa índices (0, 1, 2...) y el valor es numérico,
                # intentar usar el valor como índice directamente
                if isinstance(value, (int, np.integer)):
                    # Si el mapeo tiene claves numéricas (índices), usar el valor como índice
                    if any(isinstance(k, (int, np.integer)) for k in mapping.keys()):
                        # El valor puede ser un índice de staging (0, 1, 2...) o un ID del CSV
                        # Intentar primero como índice directo
                        if value in mapping:
                            return mapping[value]
                        # Si el valor es un índice válido en staging, mapear por posición
                        if 0 <= value < len(df_staging_target) and value in position_mapping:
                            return position_mapping[value]
                        # Si el valor parece ser un índice (0-based), intentar mapear
                        if 0 <= value < len(df_production_target):
                            if target_id_col in df_production_target.columns:
                                return int(df_production_target.iloc[value][target_id_col])
                
                # Mantener valor original si no se puede mapear
                return value
            
            # Aplicar mapeo
            df_resolved[fk_column] = [
                map_fk(val, idx) for idx, val in enumerate(df_resolved[fk_column])
            ]
            
            print(f"      ✓ Foreign key '{fk_column}' resuelta")
            
        except Exception as e:
            print(f"      ⚠ Error al resolver FK '{fk_column}': {str(e)}")
            # Mantener valores originales en caso de error
    
    return df_resolved


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def load_to_production(
    source_table: str,
    target_table: str,
    natural_keys: Optional[List[str]] = None,
    foreign_keys: Optional[Dict[str, str]] = None,
    id_mappings: Optional[Dict[str, Dict[Any, int]]] = None,
    create_position_mapping: bool = False
) -> Tuple[int, Dict[Any, int]]:
    """
    Transfiere datos desde una tabla staging a una tabla de producción.
    
    Args:
        source_table: Nombre de la tabla staging (ej: 'usuarios_raw')
        target_table: Nombre de la tabla de producción (ej: 'usuarios')
        natural_keys: Lista de columnas que forman identificador natural (para mapeo)
        foreign_keys: Diccionario {fk_column: target_table} para resolver FKs
        id_mappings: Diccionario de mapeos de IDs ya creados {table_name: {staging_id: production_id}}
        
    Returns:
        Tupla (filas_insertadas, mapeo_de_ids)
        - filas_insertadas: Número de filas insertadas
        - mapeo_de_ids: Diccionario mapeando identificadores naturales -> IDs de producción
    """
    db = DBConnector.get_instance()
    engine = db.get_engine()
    
    print(f"\n{'='*80}")
    print(f"CARGANDO A PRODUCCIÓN: {source_table} → {target_table}")
    print(f"{'='*80}")
    
    try:
        # Leer datos de staging
        query = f"SELECT * FROM {source_table}"
        df = pd.read_sql(query, engine)
        
        if len(df) == 0:
            print(f"   ⚠ Tabla staging '{source_table}' está vacía")
            return 0, {}
        
        print(f"   ✓ Datos leídos de staging: {len(df)} filas")
        
        # Resolver foreign keys si es necesario
        if foreign_keys and id_mappings:
            print(f"   Resolviendo foreign keys...")
            df = resolve_foreign_keys(df, foreign_keys, id_mappings, engine)
        
        # Obtener el nombre real de la columna primary key desde PostgreSQL
        target_id_column = _get_primary_key_column(target_table, engine)
        
        # Filtrar columnas: solo las que existen en ambas tablas y no son IDs
        columns_to_insert = [col for col in df.columns if col != target_id_column]
        
        if not columns_to_insert:
            print(f"   ⚠ No hay columnas para insertar")
            return 0, {}
        
        # Preparar DataFrame para inserción
        df_to_insert = df[columns_to_insert].copy()
        
        # Insertar datos usando pandas to_sql
        print(f"   Insertando {len(df_to_insert)} filas en '{target_table}'...")
        df_to_insert.to_sql(
            target_table,
            engine,
            if_exists='append',
            index=False,
            method='multi'
        )
        
        filas_insertadas = len(df_to_insert)
        print(f"   ✓ {filas_insertadas} filas insertadas exitosamente")
        
        # Crear mapeo de IDs si se proporcionaron natural keys
        mapeo_ids = {}
        if natural_keys:
            print(f"   Creando mapeo de IDs usando: {natural_keys}")
            # Leer datos recién insertados para obtener los nuevos IDs
            query_target = f"SELECT * FROM {target_table} ORDER BY {target_id_column} DESC LIMIT {filas_insertadas}"
            df_inserted = pd.read_sql(query_target, engine)
            
            if len(df_inserted) > 0 and target_id_column in df_inserted.columns:
                # Crear mapeo usando natural keys
                if all(key in df.columns and key in df_inserted.columns for key in natural_keys):
                    # Crear clave natural en source
                    if len(natural_keys) == 1:
                        df['_natural_key'] = df[natural_keys[0]].astype(str)
                        df_inserted['_natural_key'] = df_inserted[natural_keys[0]].astype(str)
                    else:
                        df['_natural_key'] = df[natural_keys].apply(
                            lambda row: '|'.join(row.astype(str)), axis=1
                        )
                        df_inserted['_natural_key'] = df_inserted[natural_keys].apply(
                            lambda row: '|'.join(row.astype(str)), axis=1
                        )
                    
                    # Hacer merge para obtener mapeo
                    merged = df.merge(
                        df_inserted[[target_id_column, '_natural_key']],
                        on='_natural_key',
                        how='left'
                    )
                    
                    # Crear diccionario de mapeo
                    for _, row in merged.iterrows():
                        if pd.notna(row[target_id_column]):
                            natural_key_value = row['_natural_key']
                            mapeo_ids[natural_key_value] = int(row[target_id_column])
        elif create_position_mapping:
            # Si no hay natural keys pero la tabla es referenciada por otras (necesita mapeo),
            # crear mapeo por posición: posición en staging -> ID en producción
            # Esto es útil cuando el orden se mantiene entre staging y producción
            print(f"   Creando mapeo de IDs por posición (índice -> ID)")
            query_target = f"SELECT {target_id_column} FROM {target_table} ORDER BY {target_id_column} LIMIT {filas_insertadas}"
            df_inserted = pd.read_sql(query_target, engine)
            
            if len(df_inserted) > 0 and target_id_column in df_inserted.columns:
                # Crear mapeo: índice en staging (0, 1, 2, ...) -> ID en producción
                # También mapear valores 1-based (1, 2, 3...) -> ID en producción
                # porque en staging los valores pueden venir como 1, 2, 3... del CSV
                for idx in range(min(len(df), len(df_inserted))):
                    production_id = int(df_inserted.iloc[idx][target_id_column])
                    # Usar el índice 0-based como clave (0 -> ID1, 1 -> ID2, etc.)
                    mapeo_ids[idx] = production_id
                    # También mapear índice 1-based (1 -> ID1, 2 -> ID2, etc.)
                    # para cuando los valores en staging vienen como 1, 2, 3...
                    mapeo_ids[idx + 1] = production_id
        
        print(f"{'='*80}\n")
        return filas_insertadas, mapeo_ids
        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"✗ ERROR al cargar {source_table} → {target_table}: {str(e)}")
        print(f"{'='*80}\n")
        raise


def load_all_to_production(load_order: Optional[List[Tuple]] = None) -> Dict[str, Dict[Any, int]]:
    """
    Carga todas las tablas staging a producción respetando el orden de dependencias.
    
    Args:
        load_order: Lista de tuplas (source_table, target_table, natural_keys, foreign_keys)
                   Si None, usa LOAD_ORDER por defecto
        
    Returns:
        Diccionario con mapeos de IDs por tabla: {table_name: {natural_key: production_id}}
    """
    if load_order is None:
        load_order = LOAD_ORDER
    
    # Identificar qué tablas son referenciadas por otras (necesitan mapeo)
    # Esto determina si una tabla sin natural_keys necesita mapeo por posición
    referenced_tables = set()
    for table_config in load_order:
        if len(table_config) >= 4:
            _, _, _, foreign_keys = table_config[:4]
            if foreign_keys:
                for target_table_fk in foreign_keys.values():
                    referenced_tables.add(target_table_fk)
    
    db = DBConnector.get_instance()
    engine = db.get_engine()
    
    print(f"\n{'='*80}")
    print("INICIANDO CARGA COMPLETA A PRODUCCIÓN")
    print(f"{'='*80}")
    
    id_mappings = {}  # {table_name: {natural_key: production_id}}
    all_id_mappings = {}  # Para resolver foreign keys
    
    for i, table_config in enumerate(load_order, 1):
        if len(table_config) == 3:
            source_table, target_table, natural_keys = table_config
            foreign_keys = None
        elif len(table_config) == 4:
            source_table, target_table, natural_keys, foreign_keys = table_config
        else:
            continue
        
        print(f"\n[{i}/{len(load_order)}] Procesando: {source_table} → {target_table}")
        
        # Determinar si necesita mapeo por posición:
        # 1. Si tiene natural_keys, siempre crea mapeo (manejado internamente)
        # 2. Si no tiene natural_keys pero es referenciada por otras tablas, crea mapeo por posición
        needs_position_mapping = natural_keys is None and target_table in referenced_tables
        
        # Resolver foreign keys usando mapeos anteriores
        fk_mappings_for_resolution = {}
        if foreign_keys:
            for fk_col, target_table_fk in foreign_keys.items():
                if target_table_fk in all_id_mappings:
                    fk_mappings_for_resolution[fk_col] = target_table_fk
        
        # Cargar a producción
        filas, mapeo = load_to_production(
            source_table=source_table,
            target_table=target_table,
            natural_keys=natural_keys,
            foreign_keys=foreign_keys,
            id_mappings=all_id_mappings if foreign_keys else None,
            create_position_mapping=needs_position_mapping
        )
        
        # Guardar mapeo
        if mapeo:
            id_mappings[target_table] = mapeo
            all_id_mappings[target_table] = mapeo
    
    print(f"\n{'='*80}")
    print("✓ CARGA COMPLETA A PRODUCCIÓN FINALIZADA")
    print(f"{'='*80}\n")
    
    return id_mappings

