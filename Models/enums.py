"""
Enumeraciones para los campos de estado en las tablas.
Extraídas de los archivos CSV para preservar la integridad semántica.
"""

from enum import Enum


class EstadoOrden(str, Enum):
    """
    Enum para los estados de una orden.
    Valores extraídos de 5.ordenes.csv
    """
    PENDIENTE = 'Pendiente'
    ENVIADO = 'Enviado'
    COMPLETADO = 'Completado'
    CANCELADO = 'Cancelado'


class EstadoPago(str, Enum):
    """
    Enum para los estados de un pago.
    Valores extraídos de 12.historial_pagos.csv
    """
    PROCESANDO = 'Procesando'
    PAGADO = 'Pagado'
    FALLIDO = 'Fallido'
    REEMBOLSADO = 'Reembolsado'

