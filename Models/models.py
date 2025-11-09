"""
Modelos ORM de SQLAlchemy para definir la estructura de las tablas en PostgreSQL.
Adaptado desde el DDL original de SQL Server a PostgreSQL.
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
    """Modelo ORM para la tabla usuarios"""
    __tablename__ = 'usuarios'
    
    usuario_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    dni = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())


class Categoria(Base):
    """Modelo ORM para la tabla categorias"""
    __tablename__ = 'categorias'
    
    categoria_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))


class Producto(Base):
    """Modelo ORM para la tabla productos"""
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
    """Modelo ORM para la tabla ordenes"""
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
    """Modelo ORM para la tabla detalle_ordenes"""
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
    """Modelo ORM para la tabla direcciones_envio"""
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
    """Modelo ORM para la tabla carrito"""
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
    """Modelo ORM para la tabla metodos_pago"""
    __tablename__ = 'metodos_pago'
    
    metodo_pago_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))


class OrdenMetodoPago(Base):
    """Modelo ORM para la tabla ordenes_metodos_pago"""
    __tablename__ = 'ordenes_metodos_pago'
    __table_args__ = (
        CheckConstraint('monto_pagado >= 0', name='check_monto_pagado_positivo'),
    )
    
    orden_metodo_id = Column(Integer, primary_key=True, autoincrement=True)
    orden_id = Column(Integer, ForeignKey('ordenes.orden_id'))
    metodo_pago_id = Column(Integer, ForeignKey('metodos_pago.metodo_pago_id'))
    monto_pagado = Column(Numeric(10, 2), nullable=False)


class ResenaProducto(Base):
    """Modelo ORM para la tabla resenas_productos"""
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
    """Modelo ORM para la tabla historial_pagos"""
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