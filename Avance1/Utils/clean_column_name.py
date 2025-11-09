"""
Módulo para limpiar y estandarizar nombres de columnas.
Convierte camelCase a snake_case y minúsculas.
"""

import re


def clean_column_name(column_name: str) -> str:
    """
    Estandariza los nombres de columnas a minúsculas y snake_case.
    Convierte camelCase (ej: OrdenID, UsuarioID) a snake_case (ej: orden_id, usuario_id).
    
    Args:
        column_name: Nombre de la columna a limpiar
        
    Returns:
        str: Nombre de columna estandarizado en snake_case y minúsculas
    """
    # Insertar guiones bajos antes de transiciones de minúscula/número a mayúscula
    # Esto convierte camelCase a snake_case: OrdenID -> Orden_ID
    column_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', column_name)
    
    # Insertar guiones bajos antes de transiciones de mayúscula a mayúscula seguida de minúscula
    # Esto maneja casos como "ID" seguido de otra palabra: OrdenID -> Orden_ID (ya manejado arriba)
    # Pero también maneja casos como "XMLParser" -> "XML_Parser"
    column_name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', column_name)
    
    # Reemplazar espacios y caracteres especiales por guiones bajos
    column_name = re.sub(r'[^\w]', '_', column_name)
    
    # Convertir todo a minúsculas
    column_name = column_name.lower()
    
    # Eliminar guiones bajos múltiples
    column_name = re.sub(r'_+', '_', column_name)
    
    # Eliminar guiones bajos al inicio y final
    column_name = column_name.strip('_')
    
    return column_name