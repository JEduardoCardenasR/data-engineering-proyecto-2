"""
Módulo de transformaciones y limpieza de datos para tablas STAGING.
Aplica transformaciones basadas en el análisis exploratorio de datos (EDA).

Las transformaciones se aplican sobre datos en tablas staging antes de cargar a producción.
"""

import os
import sys
import re
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from datetime import datetime

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
# FUNCIONES GENÉRICAS DE TRANSFORMACIÓN
# ============================================================================

def apply_trim(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Aplica trim (elimina espacios al inicio y final) a columnas de texto.
    
    Args:
        df: DataFrame a transformar
        columns: Lista de nombres de columnas a las que aplicar trim
        
    Returns:
        DataFrame con columnas trimadas
    """
    df_transformed = df.copy()
    
    for col in columns:
        if col in df_transformed.columns:
            # Aplicar trim solo a valores no nulos
            df_transformed[col] = df_transformed[col].astype(str).str.strip()
            # Reemplazar strings vacíos con NaN
            df_transformed[col] = df_transformed[col].replace('', np.nan)
            # Reemplazar 'nan' string con NaN
            df_transformed[col] = df_transformed[col].replace('nan', np.nan)
    
    return df_transformed


def normalize_emails(email: str) -> str:
    """
    Normaliza un email eliminando espacios, normalizando acentos y caracteres especiales.
    
    Args:
        email: Email a normalizar
        
    Returns:
        Email normalizado
    """
    if pd.isna(email) or email == '':
        return email
    
    email_str = str(email)
    
    # Convertir a minúsculas
    email_str = email_str.lower()
    
    # Eliminar espacios
    email_str = email_str.replace(' ', '')
    
    # Normalizar acentos y caracteres especiales
    # Reemplazar caracteres acentuados por sus equivalentes sin acento
    replacements = {
        'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a',
        'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i',
        'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o',
        'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u',
        'ñ': 'n', 'ç': 'c'
    }
    
    for old, new in replacements.items():
        email_str = email_str.replace(old, new)
    
    # Filtrar caracteres especiales inválidos (mantener solo letras, números, @, ., _, -)
    email_str = re.sub(r'[^a-z0-9@._-]', '', email_str)
    
    # Validar formato básico de email
    email_pattern = r'^[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    if not re.match(email_pattern, email_str):
        # Si no cumple el formato, intentar corregir
        # Separar por @
        parts = email_str.split('@')
        if len(parts) == 2:
            local, domain = parts
            # Limpiar local y domain
            local = re.sub(r'[^a-z0-9._-]', '', local)
            domain = re.sub(r'[^a-z0-9.-]', '', domain)
            email_str = f"{local}@{domain}"
    
    return email_str


def remove_duplicates_by_key(
    df: pd.DataFrame,
    key_columns: List[str],
    keep: str = 'last',
    sort_column: Optional[str] = None
) -> pd.DataFrame:
    """
    Elimina duplicados basándose en columnas clave, manteniendo el registro especificado.
    
    Args:
        df: DataFrame a limpiar
        key_columns: Lista de columnas que forman la clave única
        keep: 'first', 'last', o False (eliminar todos los duplicados)
        sort_column: Columna para ordenar antes de eliminar (opcional)
        
    Returns:
        DataFrame sin duplicados
    """
    df_clean = df.copy()
    
    # Ordenar si se especifica una columna de ordenamiento
    if sort_column and sort_column in df_clean.columns:
        df_clean = df_clean.sort_values(by=sort_column)
    
    # Eliminar duplicados
    df_clean = df_clean.drop_duplicates(subset=key_columns, keep=keep)
    
    return df_clean


# ============================================================================
# FUNCIONES DE TRANSFORMACIÓN POR TABLA
# ============================================================================

def transform_usuarios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma la tabla usuarios_raw aplicando normalizaciones.
    
    Transformaciones aplicadas:
    - Trim a nombre, apellido, dni
    - Normalización de emails (eliminación de espacios, acentos, caracteres especiales)
    - Validación de formato de email
    
    Args:
        df: DataFrame de usuarios_raw
        
    Returns:
        DataFrame transformado
    """
    print("   Aplicando transformaciones a usuarios...")
    df_transformed = df.copy()
    
    # Aplicar trim a campos de texto
    text_columns = ['nombre', 'apellido', 'dni']
    df_transformed = apply_trim(df_transformed, text_columns)
    
    # Normalizar emails
    if 'email' in df_transformed.columns:
        print(f"      Normalizando {df_transformed['email'].notna().sum()} emails...")
        df_transformed['email'] = df_transformed['email'].apply(normalize_emails)
        
        # Contar emails corregidos
        if 'email' in df.columns:
            emails_corregidos = (df['email'] != df_transformed['email']).sum()
            if emails_corregidos > 0:
                print(f"      ✓ {emails_corregidos} emails normalizados")
    
    print("   ✓ Transformación de usuarios completada")
    return df_transformed


def transform_categorias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma la tabla categorias_raw aplicando normalizaciones.
    
    Transformaciones aplicadas:
    - Trim a nombre y descripcion
    
    Args:
        df: DataFrame de categorias_raw
        
    Returns:
        DataFrame transformado
    """
    print("   Aplicando transformaciones a categorias...")
    df_transformed = df.copy()
    
    # Aplicar trim a campos de texto
    text_columns = ['nombre', 'descripcion']
    df_transformed = apply_trim(df_transformed, text_columns)
    
    print("   ✓ Transformación de categorias completada")
    return df_transformed


def transform_productos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma la tabla productos_raw aplicando normalizaciones.
    
    Transformaciones aplicadas:
    - Trim a nombre y descripcion
    - Validación de precios y stock (no negativos)
    
    Args:
        df: DataFrame de productos_raw
        
    Returns:
        DataFrame transformado
    """
    print("   Aplicando transformaciones a productos...")
    df_transformed = df.copy()
    
    # Aplicar trim a campos de texto
    text_columns = ['nombre', 'descripcion']
    df_transformed = apply_trim(df_transformed, text_columns)
    
    # Validar precios y stock (asegurar que no sean negativos)
    if 'precio' in df_transformed.columns:
        negativos = (df_transformed['precio'] < 0).sum()
        if negativos > 0:
            print(f"      ⚠ Advertencia: {negativos} productos con precio negativo encontrados")
            df_transformed.loc[df_transformed['precio'] < 0, 'precio'] = 0
    
    if 'stock' in df_transformed.columns:
        negativos = (df_transformed['stock'] < 0).sum()
        if negativos > 0:
            print(f"      ⚠ Advertencia: {negativos} productos con stock negativo encontrados")
            df_transformed.loc[df_transformed['stock'] < 0, 'stock'] = 0
    
    print("   ✓ Transformación de productos completada")
    return df_transformed


def transform_ordenes(df: pd.DataFrame, df_detalle_ordenes: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Transforma la tabla ordenes_raw aplicando normalizaciones y cálculos.
    
    Transformaciones aplicadas:
    - Cálculo de totales desde detalle_ordenes (si se proporciona)
    - Validación de totales (no negativos)
    
    Args:
        df: DataFrame de ordenes_raw
        df_detalle_ordenes: DataFrame de detalle_ordenes_raw (opcional) para calcular totales
        
    Returns:
        DataFrame transformado
    """
    print("   Aplicando transformaciones a ordenes...")
    df_transformed = df.copy()
    
    # Si se proporciona detalle_ordenes, calcular totales
    if df_detalle_ordenes is not None and 'orden_id' in df_detalle_ordenes.columns:
        print("      Calculando totales desde detalle_ordenes...")
        
        # Calcular subtotal por orden
        if 'cantidad' in df_detalle_ordenes.columns and 'precio_unitario' in df_detalle_ordenes.columns:
            df_detalle_ordenes_copy = df_detalle_ordenes.copy()
            df_detalle_ordenes_copy['subtotal'] = (
                df_detalle_ordenes_copy['cantidad'] * df_detalle_ordenes_copy['precio_unitario']
            )
            
            # Agrupar por orden_id y sumar
            totales_por_orden = df_detalle_ordenes_copy.groupby('orden_id')['subtotal'].sum().reset_index()
            totales_por_orden.columns = ['orden_id', 'total_calculado']
            
            # IMPORTANTE: ordenes_raw NO tiene orden_id (es staging sin IDs)
            # Usamos el índice del DataFrame como identificador temporal
            # Asumimos que las órdenes están en el mismo orden que en el CSV
            # (orden_id 1 = índice 0, orden_id 2 = índice 1, etc.)
            
            # Crear un índice temporal basado en la posición (0-indexed)
            # que corresponde al orden_id (1-indexed)
            df_transformed = df_transformed.reset_index(drop=True)
            df_transformed['_temp_orden_index'] = df_transformed.index + 1  # +1 porque orden_id empieza en 1
            
            # Hacer merge usando el índice temporal
            df_transformed = df_transformed.merge(
                totales_por_orden,
                left_on='_temp_orden_index',
                right_on='orden_id',
                how='left'
            )
            
            # Actualizar total con el calculado
            if 'total' in df_transformed.columns:
                # Usar el total calculado si existe, sino mantener el original
                df_transformed['total'] = df_transformed['total_calculado'].fillna(df_transformed['total'])
                # Eliminar columnas temporales y orden_id (no debe estar en ordenes_raw)
                columns_to_drop = ['total_calculado', '_temp_orden_index']
                if 'orden_id' in df_transformed.columns:
                    columns_to_drop.append('orden_id')
                df_transformed = df_transformed.drop(columns=columns_to_drop)
                
                # Contar inconsistencias corregidas
                if 'total' in df.columns:
                    # Comparar redondeando a 2 decimales para evitar problemas de precisión
                    df_original = df['total'].round(2)
                    df_nuevo = df_transformed['total'].round(2)
                    inconsistencias = (df_original != df_nuevo).sum()
                    if inconsistencias > 0:
                        print(f"      ✓ {inconsistencias} totales de órdenes corregidos")
                    else:
                        print(f"      ✓ Total de órdenes verificado (todos coinciden con detalle_ordenes)")
    
    # Validar totales (asegurar que no sean negativos)
    if 'total' in df_transformed.columns:
        negativos = (df_transformed['total'] < 0).sum()
        if negativos > 0:
            print(f"      ⚠ Advertencia: {negativos} órdenes con total negativo encontrados")
            df_transformed.loc[df_transformed['total'] < 0, 'total'] = 0
    
    print("   ✓ Transformación de ordenes completada")
    return df_transformed


def transform_detalle_ordenes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma la tabla detalle_ordenes_raw aplicando validaciones.
    
    Transformaciones aplicadas:
    - Validación de cantidad y precio_unitario (no negativos)
    
    Args:
        df: DataFrame de detalle_ordenes_raw
        
    Returns:
        DataFrame transformado
    """
    print("   Aplicando transformaciones a detalle_ordenes...")
    df_transformed = df.copy()
    
    # Validar cantidad y precio_unitario (asegurar que no sean negativos)
    if 'cantidad' in df_transformed.columns:
        negativos = (df_transformed['cantidad'] < 0).sum()
        if negativos > 0:
            print(f"      ⚠ Advertencia: {negativos} detalles con cantidad negativa encontrados")
            df_transformed.loc[df_transformed['cantidad'] < 0, 'cantidad'] = 0
    
    if 'precio_unitario' in df_transformed.columns:
        negativos = (df_transformed['precio_unitario'] < 0).sum()
        if negativos > 0:
            print(f"      ⚠ Advertencia: {negativos} detalles con precio_unitario negativo encontrados")
            df_transformed.loc[df_transformed['precio_unitario'] < 0, 'precio_unitario'] = 0
    
    print("   ✓ Transformación de detalle_ordenes completada")
    return df_transformed


def transform_resenas_productos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma la tabla resenas_productos_raw eliminando duplicados.
    
    Transformaciones aplicadas:
    - Eliminación de duplicados por (usuario_id, producto_id)
    - Mantiene la reseña más reciente (por fecha o por orden de aparición)
    
    Args:
        df: DataFrame de resenas_productos_raw
        
    Returns:
        DataFrame transformado sin duplicados
    """
    print("   Aplicando transformaciones a resenas_productos...")
    df_transformed = df.copy()
    
    registros_antes = len(df_transformed)
    
    # Eliminar duplicados por usuario_id y producto_id
    # Mantener la más reciente (por fecha si existe, sino por orden de aparición)
    key_columns = ['usuario_id', 'producto_id']
    
    if all(col in df_transformed.columns for col in key_columns):
        # Ordenar por fecha si existe
        sort_column = 'fecha' if 'fecha' in df_transformed.columns else None
        
        df_transformed = remove_duplicates_by_key(
            df_transformed,
            key_columns=key_columns,
            keep='last',
            sort_column=sort_column
        )
        
        duplicados_eliminados = registros_antes - len(df_transformed)
        if duplicados_eliminados > 0:
            print(f"      ✓ {duplicados_eliminados} reseñas duplicadas eliminadas")
    
    print("   ✓ Transformación de resenas_productos completada")
    return df_transformed


def transform_direcciones_envio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma la tabla direcciones_envio_raw aplicando normalizaciones.
    
    Transformaciones aplicadas:
    - Trim a todos los campos de texto
    
    Args:
        df: DataFrame de direcciones_envio_raw
        
    Returns:
        DataFrame transformado
    """
    print("   Aplicando transformaciones a direcciones_envio...")
    df_transformed = df.copy()
    
    # Aplicar trim a todos los campos de texto
    text_columns = ['calle', 'ciudad', 'departamento', 'provincia', 'distrito', 'estado', 'codigo_postal', 'pais']
    df_transformed = apply_trim(df_transformed, text_columns)
    
    print("   ✓ Transformación de direcciones_envio completada")
    return df_transformed


def transform_metodos_pago(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma la tabla metodos_pago_raw aplicando normalizaciones.
    
    Transformaciones aplicadas:
    - Trim a nombre y descripcion
    
    Args:
        df: DataFrame de metodos_pago_raw
        
    Returns:
        DataFrame transformado
    """
    print("   Aplicando transformaciones a metodos_pago...")
    df_transformed = df.copy()
    
    # Aplicar trim a campos de texto
    text_columns = ['nombre', 'descripcion']
    df_transformed = apply_trim(df_transformed, text_columns)
    
    print("   ✓ Transformación de metodos_pago completada")
    return df_transformed


def transform_carrito(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma la tabla carrito_raw aplicando validaciones.
    
    Transformaciones aplicadas:
    - Validación de cantidad (no negativa)
    
    Args:
        df: DataFrame de carrito_raw
        
    Returns:
        DataFrame transformado
    """
    print("   Aplicando transformaciones a carrito...")
    df_transformed = df.copy()
    
    # Validar cantidad (asegurar que no sea negativa)
    if 'cantidad' in df_transformed.columns:
        negativos = (df_transformed['cantidad'] < 0).sum()
        if negativos > 0:
            print(f"      ⚠ Advertencia: {negativos} registros con cantidad negativa encontrados")
            df_transformed.loc[df_transformed['cantidad'] < 0, 'cantidad'] = 0
    
    print("   ✓ Transformación de carrito completada")
    return df_transformed


def transform_ordenes_metodos_pago(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma la tabla ordenes_metodos_pago_raw aplicando validaciones.
    
    Transformaciones aplicadas:
    - Validación de monto_pagado (no negativo)
    
    Args:
        df: DataFrame de ordenes_metodos_pago_raw
        
    Returns:
        DataFrame transformado
    """
    print("   Aplicando transformaciones a ordenes_metodos_pago...")
    df_transformed = df.copy()
    
    # Validar monto_pagado (asegurar que no sea negativo)
    if 'monto_pagado' in df_transformed.columns:
        negativos = (df_transformed['monto_pagado'] < 0).sum()
        if negativos > 0:
            print(f"      ⚠ Advertencia: {negativos} registros con monto_pagado negativo encontrados")
            df_transformed.loc[df_transformed['monto_pagado'] < 0, 'monto_pagado'] = 0
    
    print("   ✓ Transformación de ordenes_metodos_pago completada")
    return df_transformed


def transform_historial_pagos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma la tabla historial_pagos_raw aplicando validaciones.
    
    Transformaciones aplicadas:
    - Validación de monto (no negativo)
    
    Args:
        df: DataFrame de historial_pagos_raw
        
    Returns:
        DataFrame transformado
    """
    print("   Aplicando transformaciones a historial_pagos...")
    df_transformed = df.copy()
    
    # Validar monto (asegurar que no sea negativo)
    if 'monto' in df_transformed.columns:
        negativos = (df_transformed['monto'] < 0).sum()
        if negativos > 0:
            print(f"      ⚠ Advertencia: {negativos} registros con monto negativo encontrados")
            df_transformed.loc[df_transformed['monto'] < 0, 'monto'] = 0
    
    print("   ✓ Transformación de historial_pagos completada")
    return df_transformed


# ============================================================================
# FUNCIÓN PRINCIPAL DE TRANSFORMACIÓN
# ============================================================================

def apply_transformations(table_name_raw: str, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Aplica las transformaciones correspondientes a una tabla staging.
    
    Args:
        table_name_raw: Nombre de la tabla staging (ej: 'usuarios_raw')
        df: DataFrame con datos de la tabla staging
        **kwargs: Argumentos adicionales para transformaciones específicas
                  (ej: df_detalle_ordenes para transform_ordenes)
        
    Returns:
        DataFrame transformado
        
    Raises:
        ValueError: Si la tabla no tiene función de transformación definida
    """
    transform_map = {
        'usuarios_raw': transform_usuarios,
        'categorias_raw': transform_categorias,
        'productos_raw': transform_productos,
        'ordenes_raw': transform_ordenes,
        'detalle_ordenes_raw': transform_detalle_ordenes,
        'direcciones_envio_raw': transform_direcciones_envio,
        'carrito_raw': transform_carrito,
        'metodos_pago_raw': transform_metodos_pago,
        'ordenes_metodos_pago_raw': transform_ordenes_metodos_pago,
        'resenas_productos_raw': transform_resenas_productos,
        'historial_pagos_raw': transform_historial_pagos
    }
    
    if table_name_raw not in transform_map:
        available_tables = ', '.join(transform_map.keys())
        raise ValueError(
            f"No hay función de transformación definida para '{table_name_raw}'.\n"
            f"Tablas disponibles: {available_tables}"
        )
    
    transform_func = transform_map[table_name_raw]
    
    # Aplicar transformación
    if table_name_raw == 'ordenes_raw' and 'df_detalle_ordenes' in kwargs:
        return transform_func(df, df_detalle_ordenes=kwargs['df_detalle_ordenes'])
    else:
        return transform_func(df)

