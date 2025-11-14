"""
Modelos ORM de SQLAlchemy para definir la estructura de las tablas de PRODUCCIÓN en PostgreSQL.
Adaptado desde el DDL original de SQL Server a PostgreSQL.

IMPORTANTE: Estos son modelos de PRODUCCIÓN (capa final).
- Incluyen IDs autoincrementales (primary keys)
- Incluyen foreign keys y constraints de integridad referencial
- Incluyen CHECK constraints para validación de datos
- Incluyen valores por defecto y enums tipados

Para modelos de STAGING (datos crudos), ver: models_raw.py
"""

import os
import sys
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func, text

# Import Enums
try:
    from .enums import EstadoOrden, EstadoPago
except ImportError:
    from enums import EstadoOrden, EstadoPago

# Base declarativa para los modelos ORM
Base = declarative_base()


class Usuario(Base):
    """
    Modelo ORM de PRODUCCIÓN para la tabla usuarios.
    
    Esta es la capa final con:
    - ID autoincremental (usuario_id)
    - Constraints UNIQUE en dni y email
    - Valores por defecto en fecha_registro
    """
    __tablename__ = 'usuarios'
    
    usuario_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    dni = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())


class Categoria(Base):
    """
    Modelo ORM de PRODUCCIÓN para la tabla categorias.
    
    Esta es la capa final con:
    - ID autoincremental (categoria_id)
    - Referenciada por productos (foreign key)
    """
    __tablename__ = 'categorias'
    
    categoria_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))


class Producto(Base):
    """
    Modelo ORM de PRODUCCIÓN para la tabla productos.
    
    Esta es la capa final con:
    - ID autoincremental (producto_id)
    - Foreign key a categorias
    - CHECK constraints para precio >= 0 y stock >= 0
    """
    __tablename__ = 'productos'
    __table_args__ = (
        CheckConstraint('precio >= 0', name='check_precio_positivo'),
        CheckConstraint('stock >= 0', name='check_stock_positivo'),
    )
    
    producto_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String)  # TEXT en PostgreSQL
    precio = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.categoria_id'))


class Orden(Base):
    """
    Modelo ORM de PRODUCCIÓN para la tabla ordenes.
    
    Esta es la capa final con:
    - ID autoincremental (orden_id)
    - Foreign key a usuarios
    - CHECK constraint para total >= 0
    - Enum tipado para estado
    - Valor por defecto en fecha_orden
    """
    __tablename__ = 'ordenes'
    __table_args__ = (
        CheckConstraint('total >= 0', name='check_total_positivo'),
    )
    
    orden_id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.usuario_id'))
    fecha_orden = Column(DateTime, server_default=func.now())
    total = Column(Numeric(10, 2), nullable=False)
    estado = Column(Enum(EstadoOrden, name='estado_orden', native_enum=True, values_callable=lambda x: [e.value for e in x]), server_default=text("'Pendiente'"))


class DetalleOrden(Base):
    """
    Modelo ORM de PRODUCCIÓN para la tabla detalle_ordenes.
    
    Esta es la capa final con:
    - ID autoincremental (detalle_id)
    - Foreign keys a ordenes y productos
    - CHECK constraints para cantidad >= 0 y precio_unitario >= 0
    """
    __tablename__ = 'detalle_ordenes'
    __table_args__ = (
        CheckConstraint('cantidad >= 0', name='check_cantidad_positiva'),
        CheckConstraint('precio_unitario >= 0', name='check_precio_unitario_positivo'),
    )
    
    detalle_id = Column(Integer, primary_key=True, autoincrement=True)
    orden_id = Column(Integer, ForeignKey('ordenes.orden_id'))
    producto_id = Column(Integer, ForeignKey('productos.producto_id'))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)


class DireccionEnvio(Base):
    """
    Modelo ORM de PRODUCCIÓN para la tabla direcciones_envio.
    
    Esta es la capa final con:
    - ID autoincremental (direccion_id)
    - Foreign key a usuarios
    """
    __tablename__ = 'direcciones_envio'
    
    direccion_id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.usuario_id'))
    calle = Column(String(255), nullable=False)
    ciudad = Column(String(100), nullable=False)
    departamento = Column(String(100))
    provincia = Column(String(100))
    distrito = Column(String(100))
    estado = Column(String(100))
    codigo_postal = Column(String(20))
    pais = Column(String(100), nullable=False)


class Carrito(Base):
    """
    Modelo ORM de PRODUCCIÓN para la tabla carrito.
    
    Esta es la capa final con:
    - ID autoincremental (carrito_id)
    - Foreign keys a usuarios y productos
    - CHECK constraint para cantidad >= 0
    - Valor por defecto en fecha_agregado
    """
    __tablename__ = 'carrito'
    __table_args__ = (
        CheckConstraint('cantidad >= 0', name='check_cantidad_carrito_positiva'),
    )
    
    carrito_id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.usuario_id'))
    producto_id = Column(Integer, ForeignKey('productos.producto_id'))
    cantidad = Column(Integer, nullable=False)
    fecha_agregado = Column(DateTime, server_default=func.now())


class MetodoPago(Base):
    """
    Modelo ORM de PRODUCCIÓN para la tabla metodos_pago.
    
    Esta es la capa final con:
    - ID autoincremental (metodo_pago_id)
    - Referenciada por ordenes_metodos_pago e historial_pagos (foreign keys)
    """
    __tablename__ = 'metodos_pago'
    
    metodo_pago_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))


class OrdenMetodoPago(Base):
    """
    Modelo ORM de PRODUCCIÓN para la tabla ordenes_metodos_pago.
    
    Esta es la capa final con:
    - ID autoincremental (orden_metodo_id)
    - Foreign keys a ordenes y metodos_pago
    - CHECK constraint para monto_pagado >= 0
    """
    __tablename__ = 'ordenes_metodos_pago'
    __table_args__ = (
        CheckConstraint('monto_pagado >= 0', name='check_monto_pagado_positivo'),
    )
    
    orden_metodo_id = Column(Integer, primary_key=True, autoincrement=True)
    orden_id = Column(Integer, ForeignKey('ordenes.orden_id'))
    metodo_pago_id = Column(Integer, ForeignKey('metodos_pago.metodo_pago_id'))
    monto_pagado = Column(Numeric(10, 2), nullable=False)


class ResenaProducto(Base):
    """
    Modelo ORM de PRODUCCIÓN para la tabla resenas_productos.
    
    Esta es la capa final con:
    - ID autoincremental (resena_id)
    - Foreign keys a usuarios y productos
    - CHECK constraint para calificacion entre 1 y 5
    - Valor por defecto en fecha
    """
    __tablename__ = 'resenas_productos'
    __table_args__ = (
        CheckConstraint('calificacion >= 1 AND calificacion <= 5', name='check_calificacion_rango'),
    )
    
    resena_id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.usuario_id'))
    producto_id = Column(Integer, ForeignKey('productos.producto_id'))
    calificacion = Column(Integer)
    comentario = Column(String)  # TEXT en PostgreSQL
    fecha = Column(DateTime, server_default=func.now())


class HistorialPago(Base):
    """
    Modelo ORM de PRODUCCIÓN para la tabla historial_pagos.
    
    Esta es la capa final con:
    - ID autoincremental (pago_id)
    - Foreign keys a ordenes y metodos_pago
    - CHECK constraint para monto >= 0
    - Enum tipado para estado_pago
    - Valor por defecto en fecha_pago
    """
    __tablename__ = 'historial_pagos'
    __table_args__ = (
        CheckConstraint('monto >= 0', name='check_monto_positivo'),
    )
    
    pago_id = Column(Integer, primary_key=True, autoincrement=True)
    orden_id = Column(Integer, ForeignKey('ordenes.orden_id'))
    metodo_pago_id = Column(Integer, ForeignKey('metodos_pago.metodo_pago_id'))
    monto = Column(Numeric(10, 2), nullable=False)
    fecha_pago = Column(DateTime, server_default=func.now())
    estado_pago = Column(Enum(EstadoPago, name='estado_pago', native_enum=True, values_callable=lambda x: [e.value for e in x]), server_default=text("'Procesando'"))