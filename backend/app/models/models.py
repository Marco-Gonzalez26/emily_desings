from sqlalchemy import (
    Boolean,
    Column,
    String,
    Integer,
    Numeric,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime



Base = declarative_base()


class Usuario(Base):
    """Modelo de usuarios del sistema (clientes y administradores)"""

    __tablename__ = "usuarios"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(255))
    telefono = Column(String(20))
    direccion = Column(Text)
    fecha_registro = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    fecha_ultimo_acceso = Column(DateTime)
    rol = Column(String(20), server_default="'cliente'")
    activo = Column(Boolean, default=True)
    cedula_ruc = Column(String(13), nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


    __table_args__ = (
        CheckConstraint(
            "rol IN ('cliente', 'administrador')", name="usuarios_rol_check"
        ),
    )

    # Relaciones
    tokens_sesion = relationship(
        "TokenSesion", back_populates="usuario", cascade="all, delete-orphan"
    )
    tokens_recuperacion = relationship(
        "TokenRecuperacion", back_populates="usuario", cascade="all, delete-orphan"
    )
    perfil_morfologico = relationship(
        "PerfilMorfologico",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    preferencias = relationship(
        "PreferenciasUsuario",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )
    analisis_morfologicos = relationship(
        "AnalisisMorfologico",
        back_populates="usuario",
        cascade="all, delete-orphan",
        lazy="select",
    )
    carritos = relationship(
        "Carrito", back_populates="usuario", cascade="all, delete-orphan"
    )
    ordenes = relationship("Orden", back_populates="usuario")
    productos_creados = relationship(
        "Producto",
        foreign_keys="Producto.administrador_id",
        back_populates="administrador",
    )
    historial_productos = relationship(
        "HistorialProducto",
        foreign_keys="HistorialProducto.administrador_id",
        back_populates="administrador",
    )
    historial_reportes = relationship(
        "HistorialReporte", back_populates="administrador"
    )
    recomendaciones_ia = relationship(
        "RecomendacionIA", back_populates="usuario", cascade="all, delete-orphan"
    )


class TokenSesion(Base):
    """Tokens de sesión activos de usuarios"""

    __tablename__ = "tokens_sesion"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE")
    )
    token = Column(String(500), unique=True, nullable=False)
    fecha_creacion = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    fecha_expiracion = Column(DateTime, nullable=False)
    activo = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="tokens_sesion")


class TokenRecuperacion(Base):
    """Tokens para recuperación de contraseña"""

    __tablename__ = "tokens_recuperacion"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE")
    )
    token = Column(String(500), unique=True, nullable=False)
    fecha_creacion = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    fecha_expiracion = Column(DateTime, nullable=False)
    usado = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    usuario = relationship("Usuario", back_populates="tokens_recuperacion")


class PerfilMorfologico(Base):
    """Perfil morfológico del usuario para recomendaciones personalizadas"""

    __tablename__ = "perfil_morfologico"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True
    )
    altura = Column(Numeric(5, 2))
    peso = Column(Numeric(5, 2))
    tipo_cuerpo = Column(String(50))
    fecha_ultima_actualizacion = Column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint(
            "tipo_cuerpo IN ('Triangulo', 'Triangulo Invertido', 'Rectangulo', 'Reloj de Arena', 'Ovalo')",
            name="perfil_morfologico_tipo_cuerpo_check",
        ),
    )

    usuario = relationship("Usuario", back_populates="perfil_morfologico")


# class PreferenciaEstilo(Base):
#     """Preferencias de estilo del usuario"""

#     __tablename__ = "preferencias_estilo"

#     id = Column(
#         UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
#     )
#     usuario_id = Column(
#         UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE")
#     )
#     estilo = Column(String(50))
#     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

#     __table_args__ = (
#         CheckConstraint(
#             "estilo IN ('Casual', 'Formal', 'Deportivo', 'Elegante')",
#             name="preferencias_estilo_estilo_check",
#         ),
#         UniqueConstraint(
#             "usuario_id", "estilo", name="preferencias_estilo_usuario_id_estilo_key"
#         ),
#     )

#     usuario = relationship("Usuario", back_populates="preferencias_estilo")


class AnalisisMorfologico(Base):
    """
    Historial de análisis morfológicos
    No almacenar imágenes - solo resultados del análisis
    """

    __tablename__ = "analisis_morfologico"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo_cuerpo_detectado = Column(String(50), nullable=False)
    confianza = Column(Numeric(3, 2))  # 0.00 - 1.00
    fecha_analisis = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    usuario = relationship("Usuario", back_populates="analisis_morfologicos")
    recomendaciones = relationship(
        "RecomendacionGenerada", back_populates="analisis", cascade="all, delete-orphan"
    )


class ReglasRecomendacion(Base):
    """
    Reglas que mapean tipos de cuerpo a categorías recomendadas
    Base del sistema de recomendación
    """

    __tablename__ = "reglas_recomendacion"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    tipo_cuerpo = Column(String(50), nullable=False)
    categoria_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categorias.id", ondelete="CASCADE"),
        nullable=False,
    )
    prioridad = Column(Integer, nullable=False)  # 1=alta, 2=media, 3=baja
    razon = Column(Text, nullable=False)
    evitar = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    # Relaciones
    categoria = relationship("Categoria")


class RecomendacionGenerada(Base):
    """
    Historial de productos recomendados por IA
    Permite ver las conversiones en el dashboard del admin
    """

    __tablename__ = "recomendaciones_generadas"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    analisis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analisis_morfologico.id", ondelete="CASCADE"),
        nullable=False,
    )
    producto_id = Column(
        UUID(as_uuid=True),
        ForeignKey("productos.id", ondelete="CASCADE"),
        nullable=False,
    )
    razon_ia = Column(Text)
    palabras_clave = Column(ARRAY(String))
    score = Column(Integer)
    posicion = Column(Integer)
    fue_clickeado = Column(Boolean, default=False)
    fue_agregado_carrito = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    analisis = relationship("AnalisisMorfologico", back_populates="recomendaciones")
    producto = relationship("Producto")


class Marca(Base):
    """Marcas de productos"""

    __tablename__ = "marcas"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text)
    logo_url = Column(String(500))
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    # Relaciones
    productos = relationship("Producto", back_populates="marca")


class Categoria(Base):
    """Categorías de productos"""

    __tablename__ = "categorias"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    # Relaciones
    productos = relationship("Producto", back_populates="categoria")


class Color(Base):
    """Colores disponibles para productos"""

    __tablename__ = "colores"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    nombre = Column(String(50), unique=True, nullable=False)
    codigo_hexadecimal = Column(String(7), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    # Relaciones
    inventarios = relationship("Inventario", back_populates="color")
    carrito_items = relationship("CarritoItem", back_populates="color")
    orden_items = relationship("OrdenItem", back_populates="color")


class Talla(Base):
    """Tallas disponibles para productos"""

    __tablename__ = "tallas"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    nombre = Column(String(10), unique=True, nullable=False)
    orden = Column(Integer)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    # Relaciones
    inventarios = relationship("Inventario", back_populates="talla")
    carrito_items = relationship("CarritoItem", back_populates="talla")
    orden_items = relationship("OrdenItem", back_populates="talla")


class Producto(Base):
    """Catálogo de productos"""

    __tablename__ = "productos"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    sku = Column(String(100), unique=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    precio_regular = Column(Numeric(10, 2), nullable=False)
    precio_descuento = Column(Numeric(10, 2))
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id"))
    marca_id = Column(UUID(as_uuid=True), ForeignKey("marcas.id"))
    es_nuevo = Column(Boolean, default=False)
    es_oferta = Column(Boolean, default=False)
    es_destacado = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    administrador_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint("precio_regular > 0", name="productos_precio_regular_check"),
        CheckConstraint(
            "precio_descuento IS NULL OR precio_descuento < precio_regular",
            name="productos_check",
        ),
    )

    categoria = relationship("Categoria", back_populates="productos")
    marca = relationship("Marca", back_populates="productos")
    administrador = relationship(
        "Usuario", foreign_keys=[administrador_id], back_populates="productos_creados"
    )
    imagenes = relationship(
        "ImagenProducto", back_populates="producto", cascade="all, delete-orphan"
    )
    etiquetas_morfologicas = relationship(
        "ProductoEtiquetaMorfologica",
        back_populates="producto",
        cascade="all, delete-orphan",
    )
    inventarios = relationship(
        "Inventario", back_populates="producto", cascade="all, delete-orphan"
    )
    carrito_items = relationship("CarritoItem", back_populates="producto")
    orden_items = relationship("OrdenItem", back_populates="producto")
    historial = relationship(
        "HistorialProducto", back_populates="producto", cascade="all, delete-orphan"
    )
    recomendaciones_ia = relationship(
        "RecomendacionIA", back_populates="producto", cascade="all, delete-orphan"
    )


class ImagenProducto(Base):
    """Imágenes de productos"""

    __tablename__ = "imagenes_productos"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    producto_id = Column(
        UUID(as_uuid=True), ForeignKey("productos.id", ondelete="CASCADE")
    )
    url_imagen = Column(String(500), nullable=False)
    es_principal = Column(Boolean, default=False)
    orden = Column(Integer)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    producto = relationship("Producto", back_populates="imagenes")


class ProductoEtiquetaMorfologica(Base):
    """Etiquetas morfológicas para recomendación de productos"""

    __tablename__ = "producto_etiquetas_morfologicas"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    producto_id = Column(
        UUID(as_uuid=True), ForeignKey("productos.id", ondelete="CASCADE")
    )
    tipo_cuerpo = Column(String(50))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint(
            "tipo_cuerpo IN ('Triangulo', 'Triangulo Invertido', 'Rectangulo', 'Reloj de Arena', 'Ovalo')",
            name="producto_etiquetas_morfologicas_tipo_cuerpo_check",
        ),
        UniqueConstraint(
            "producto_id",
            "tipo_cuerpo",
            name="producto_etiquetas_morfologicas_producto_id_tipo_cuerpo_key",
        ),
    )

    producto = relationship("Producto", back_populates="etiquetas_morfologicas")


class Inventario(Base):
    """Control de inventario por producto, talla y color"""

    __tablename__ = "inventario"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    producto_id = Column(
        UUID(as_uuid=True), ForeignKey("productos.id", ondelete="CASCADE")
    )
    talla_id = Column(UUID(as_uuid=True), ForeignKey("tallas.id"))
    color_id = Column(UUID(as_uuid=True), ForeignKey("colores.id"))
    stock = Column(Integer, nullable=False, default=0)
    stock_reservado = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint("stock >= 0", name="inventario_stock_check"),
        CheckConstraint(
            "stock_reservado >= 0", name="inventario_stock_reservado_check"
        ),
        UniqueConstraint(
            "producto_id",
            "talla_id",
            "color_id",
            name="inventario_producto_id_talla_id_color_id_key",
        ),
    )

    # Relaciones
    producto = relationship("Producto", back_populates="inventarios")
    talla = relationship("Talla", back_populates="inventarios")
    color = relationship("Color", back_populates="inventarios")


class Carrito(Base):
    """Carritos de compra de usuarios"""

    __tablename__ = "carritos"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE")
    )
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint("usuario_id", "activo", name="carritos_usuario_id_activo_key"),
    )

    # Relaciones
    usuario = relationship("Usuario", back_populates="carritos")
    items = relationship(
        "CarritoItem", back_populates="carrito", cascade="all, delete-orphan"
    )


class CarritoItem(Base):
    """Items dentro del carrito de compra"""

    __tablename__ = "carrito_items"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    carrito_id = Column(
        UUID(as_uuid=True), ForeignKey("carritos.id", ondelete="CASCADE")
    )
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"))
    talla_id = Column(UUID(as_uuid=True), ForeignKey("tallas.id"))
    color_id = Column(UUID(as_uuid=True), ForeignKey("colores.id"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="carrito_items_cantidad_check"),
    )

    # Relaciones
    carrito = relationship("Carrito", back_populates="items")
    producto = relationship("Producto", back_populates="carrito_items")
    talla = relationship("Talla", back_populates="carrito_items")
    color = relationship("Color", back_populates="carrito_items")


class Orden(Base):
    """Órdenes de compra"""

    __tablename__ = "ordenes"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    numero_orden = Column(String(50), unique=True, nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    direccion_envio = Column(Text, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    costo_envio = Column(Numeric(10, 2), default=0)
    impuestos = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(50), server_default="'Confirmado'")
    metodo_pago = Column(String(50))
    stripe_payment_id = Column(String(255))
    motivo_cancelacion = Column(Text)
    fecha_orden = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    fecha_actualizacion_estado = Column(DateTime)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint(
            "estado IN ('Pendiente', 'Confirmado', 'En Proceso', 'Enviado', 'Entregado', 'Cancelado')",
            name="ordenes_estado_check",
        ),
    )

    # Relaciones
    usuario = relationship("Usuario", back_populates="ordenes")
    items = relationship(
        "OrdenItem", back_populates="orden", cascade="all, delete-orphan"
    )
    comprobante = relationship(
        "Comprobante",
        back_populates="orden",
        uselist=False,
        cascade="all, delete-orphan",
    )


class OrdenItem(Base):
    """Items de una orden de compra"""

    __tablename__ = "orden_items"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    orden_id = Column(UUID(as_uuid=True), ForeignKey("ordenes.id", ondelete="CASCADE"))
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"))
    nombre_producto = Column(String(255), nullable=False)
    talla_id = Column(UUID(as_uuid=True), ForeignKey("tallas.id"))
    color_id = Column(UUID(as_uuid=True), ForeignKey("colores.id"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="orden_items_cantidad_check"),
    )

    # Relaciones
    orden = relationship("Orden", back_populates="items")
    producto = relationship("Producto", back_populates="orden_items")
    talla = relationship("Talla", back_populates="orden_items")
    color = relationship("Color", back_populates="orden_items")


class Comprobante(Base):
    """Comprobantes de pago/factura en PDF"""

    __tablename__ = "comprobantes"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    orden_id = Column(
        UUID(as_uuid=True), ForeignKey("ordenes.id", ondelete="CASCADE"), unique=True
    )
    url_pdf = Column(String(500), nullable=False)
    fecha_generacion = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    orden = relationship("Orden", back_populates="comprobante")


class HistorialProducto(Base):
    """Auditoría de cambios en productos"""

    __tablename__ = "historial_productos"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    producto_id = Column(
        UUID(as_uuid=True), ForeignKey("productos.id", ondelete="CASCADE")
    )
    administrador_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    tipo_modificacion = Column(String(50))
    datos_anteriores = Column(JSONB)
    datos_nuevos = Column(JSONB)
    fecha_modificacion = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint(
            "tipo_modificacion IN ('Creacion', 'Modificacion', 'Eliminacion')",
            name="historial_productos_tipo_modificacion_check",
        ),
    )

    # Relaciones
    producto = relationship("Producto", back_populates="historial")
    administrador = relationship(
        "Usuario", foreign_keys=[administrador_id], back_populates="historial_productos"
    )


class RecomendacionIA(Base):
    """Recomendaciones generadas por IA para usuarios"""

    __tablename__ = "recomendaciones_ia"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE")
    )
    producto_id = Column(
        UUID(as_uuid=True), ForeignKey("productos.id", ondelete="CASCADE")
    )
    score = Column(Numeric(5, 4))
    razon_recomendacion = Column(Text)
    fecha_generacion = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    # Relaciones
    usuario = relationship("Usuario", back_populates="recomendaciones_ia")
    producto = relationship("Producto", back_populates="recomendaciones_ia")


class HistorialReporte(Base):
    """Historial de reportes generados por administradores"""

    __tablename__ = "historial_reportes"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    administrador_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    tipo_reporte = Column(String(100))
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    filtros_aplicados = Column(JSONB)
    fecha_generacion = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    administrador = relationship("Usuario", back_populates="historial_reportes")
