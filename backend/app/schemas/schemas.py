from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class UsuarioBase(BaseModel):
    """Esquema base de usuario"""

    cedula_ruc: Optional[str] = None
    email: EmailStr
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    """Esquema para crear usuario"""

    password: str = Field(..., min_length=8)
    rol: Optional[str] = "cliente"


class UsuarioUpdate(BaseModel):
    """Esquema para actualizar usuario"""

    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

    cedula_ruc: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    """Esquema de respuesta de usuario"""

    id: UUID
    rol: str
    activo: bool
    fecha_registro: datetime
    fecha_ultimo_acceso: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProductoBase(BaseModel):
    """Esquema base de producto"""

    sku: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    precio_regular: Decimal = Field(..., gt=0)
    precio_descuento: Optional[Decimal] = None

    @field_validator("precio_descuento")
    @classmethod
    def validar_descuento(cls, v, info):
        precio = info.data.get("precio_regular")
        if v is not None and precio is not None and v >= precio:
            raise ValueError("precio_descuento debe ser menor al precio_regular")
        return v

    categoria_id: Optional[UUID] = None
    marca_id: Optional[UUID] = None
    es_nuevo: bool = False
    es_oferta: bool = False
    es_destacado: bool = False

    activo: bool = True


class ProductoCreate(ProductoBase):
    """Esquema para crear producto"""

    pass


class ProductoUpdate(BaseModel):
    """Esquema para actualizar producto"""

    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_regular: Optional[Decimal] = Field(None, gt=0)
    precio_descuento: Optional[Decimal] = None
    activo: Optional[bool] = None
    es_nuevo: Optional[bool] = None
    es_oferta: Optional[bool] = None
    es_destacado: Optional[bool] = None


class ImagenProductoCreate(BaseModel):
    """Schema para crear una imagen de producto"""

    url_imagen: str
    es_principal: Optional[bool] = False
    orden: Optional[int] = None


class ImagenProductoUpdate(BaseModel):
    """Schema para actualizar una imagen de producto"""

    url_imagen: Optional[str] = None
    es_principal: Optional[bool] = None
    orden: Optional[int] = None


class ImagenProductoResponse(BaseModel):
    """Respuesta de imagen de producto"""

    id: UUID
    url_imagen: str
    es_principal: bool
    orden: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ProductoResponse(ProductoBase):
    """Esquema de respuesta de producto"""

    id: UUID
    fecha_creacion: datetime
    created_at: datetime
    updated_at: datetime
    imagenes: List[ImagenProductoResponse] = []
    tiene_stock: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class ProductoDetailResponse(ProductoResponse):
    """Respuesta detallada de producto con más información"""

    administrador_id: Optional[UUID] = None

    # categoria: Optional[CategoriaResponse] = None
    # marca: Optional[MarcaResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ProductoListResponse(BaseModel):
    """Respuesta paginada de productos"""

    total: int
    page: int
    page_size: int
    productos: List[ProductoResponse]


class ProductoFilter(BaseModel):
    """Filtros para búsqueda de productos"""

    categoria_id: Optional[UUID] = None
    marca_id: Optional[UUID] = None
    precio_min: Optional[Decimal] = None
    precio_max: Optional[Decimal] = None
    es_nuevo: Optional[bool] = None
    es_oferta: Optional[bool] = None
    es_destacado: Optional[bool] = None
    activo: Optional[bool] = True
    search: Optional[str] = None


class TallaBase(BaseModel):
    nombre: str

    orden: int = 0
    activo: bool = True


class TallaCreate(TallaBase):
    pass


class TallaUpdate(BaseModel):
    nombre: Optional[str] = None

    orden: Optional[int] = None
    activo: Optional[bool] = None


class TallaResponse(TallaBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ColorBase(BaseModel):
    nombre: str
    codigo_hexadecimal: Optional[str] = None
    activo: bool = True


class ColorCreate(ColorBase):
    pass


class ColorUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo_hexadecimal: Optional[str] = None
    activo: Optional[bool] = None


class ColorResponse(ColorBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CarritoItemBase(BaseModel):
    """Esquema base de item de carrito"""

    producto_id: UUID
    talla_id: UUID
    color_id: UUID
    cantidad: int = Field(..., gt=0)
    precio_unitario: Decimal


class CarritoItemCreate(CarritoItemBase):
    """Esquema para agregar item al carrito"""

    carrito_id: UUID


class CarritoItemResponse(BaseModel):
    """Esquema de respuesta de item de carrito"""

    id: UUID
    carrito_id: UUID
    producto_id: UUID
    talla_id: UUID
    color_id: UUID
    cantidad: int
    precio_unitario: Decimal
    producto: Optional["ProductoResponse"] = None
    created_at: datetime
    talla: Optional[TallaResponse] = None

    color: Optional[ColorResponse] = None

    model_config = ConfigDict(from_attributes=True)


class CarritoResponse(BaseModel):
    """Esquema de respuesta de carrito"""

    id: UUID
    usuario_id: UUID
    activo: bool
    created_at: datetime
    items: List[CarritoItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class OrdenItemBase(BaseModel):
    """Esquema base de item de orden"""

    producto_id: UUID
    nombre_producto: str
    talla_id: UUID
    color_id: UUID
    cantidad: int = Field(..., gt=0)
    precio_unitario: Decimal
    subtotal: Decimal


class OrdenItemCreate(BaseModel):
    producto_id: UUID
    nombre_producto: str
    talla_id: UUID
    color_id: UUID
    cantidad: int = Field(..., gt=0)
    precio_unitario: Decimal
    subtotal: Decimal


class OrdenItemResponse(BaseModel):
    id: UUID
    orden_id: UUID
    producto_id: UUID
    nombre_producto: str
    talla_id: UUID
    color_id: UUID
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
    producto: Optional["ProductoResponse"] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrdenCreate(BaseModel):
    direccion_envio: str
    subtotal: Decimal
    costo_envio: Decimal = Decimal("0")
    impuestos: Decimal = Decimal("0")
    total: Decimal
    metodo_pago: str
    items: List[OrdenItemCreate]


class OrdenResponse(BaseModel):
    id: UUID
    numero_orden: str
    usuario_id: UUID
    direccion_envio: str
    subtotal: Decimal
    costo_envio: Decimal
    impuestos: Decimal
    total: Decimal
    estado: str
    metodo_pago: Optional[str] = None
    stripe_payment_id: Optional[str] = None
    motivo_cancelacion: Optional[str] = None
    fecha_orden: datetime
    fecha_actualizacion_estado: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrdenItemResponse] = []
    usuario: Optional[UsuarioBase] = None
    model_config = ConfigDict(from_attributes=True)


class OrdenEstadoUpdate(BaseModel):
    """Schema para actualizar estado de orden (ADMIN)"""

    estado: str = Field(
        ...,
        description="Nuevo estado: Pendiente, Confirmado, En Proceso, Enviado, Entregado, Cancelado",
    )
    motivo_cancelacion: Optional[str] = Field(
        None, description="Motivo de cancelación (requerido si estado=Cancelado)"
    )


class OrdenFilters(BaseModel):
    """Filtros para búsqueda de órdenes (ADMIN)"""

    skip: int = Field(default=0, ge=0, description="Registros a saltar")
    limit: int = Field(default=50, ge=1, le=100, description="Límite de registros")
    estado: Optional[str] = Field(None, description="Filtrar por estado")
    fecha_desde: Optional[datetime] = Field(None, description="Filtrar desde fecha")
    fecha_hasta: Optional[datetime] = Field(None, description="Filtrar hasta fecha")
    search: Optional[str] = Field(
        None, description="Buscar por número de orden o email"
    )


class EstadisticasOrdenesResponse(BaseModel):
    """Estadísticas de órdenes (ADMIN)"""

    total_ordenes: int
    ordenes_por_estado: dict
    ventas_totales: float
    ordenes_mes: int
    ventas_mes: float


class StripeCheckoutRequest(BaseModel):
    """Request para crear sesión de Stripe Checkout"""

    success_url: str
    cancel_url: str


class StripeCheckoutResponse(BaseModel):
    """Response con URL de checkout de Stripe"""

    checkout_url: str
    session_id: str


class PerfilMorfologicoBase(BaseModel):
    """Esquema base de perfil morfológico"""

    altura: Optional[Decimal] = None
    peso: Optional[Decimal] = None
    tipo_cuerpo: Optional[str] = None


class PerfilMorfologicoCreate(PerfilMorfologicoBase):
    """Esquema para crear perfil morfológico"""

    usuario_id: UUID


class PerfilMorfologicoUpdate(PerfilMorfologicoBase):
    """Esquema para actualizar perfil morfológico"""

    pass


class PerfilMorfologicoResponse(PerfilMorfologicoBase):
    """Esquema de respuesta de perfil morfológico"""

    id: UUID
    usuario_id: UUID
    fecha_ultima_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)


class InventarioBase(BaseModel):
    """Esquema base de inventario"""

    producto_id: UUID
    talla_id: UUID
    color_id: UUID
    stock: int = Field(..., ge=0)
    stock_reservado: int = Field(default=0, ge=0)


class InventarioCreate(InventarioBase):
    """Esquema para crear registro de inventario"""

    pass


class InventarioUpdate(BaseModel):
    """Esquema para actualizar inventario"""

    stock: Optional[int] = Field(None, ge=0)
    stock_reservado: Optional[int] = Field(None, ge=0)


class InventarioAjuste(BaseModel):
    """Schema para ajustar stock (incrementar/decrementar)"""

    ajuste: int = Field(
        ..., description="Cantidad a ajustar (positivo=añadir, negativo=quitar)"
    )
    razon: Optional[str] = Field(None, max_length=255, description="Razón del ajuste")


class InventarioResponse(InventarioBase):
    """Esquema de respuesta de inventario"""

    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoriaBase(BaseModel):
    """Esquema base de categoría"""

    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


class CategoriaCreate(CategoriaBase):
    """Esquema para crear categoría"""

    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class CategoriaResponse(CategoriaBase):
    """Esquema de respuesta de categoría"""

    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MarcaBase(BaseModel):
    """Esquema base de marca"""

    nombre: str
    descripcion: Optional[str] = None
    logo_url: Optional[str] = None
    activo: bool = True


class MarcaCreate(MarcaBase):
    """Esquema para crear marca"""

    pass


class MarcaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class MarcaResponse(MarcaBase):
    """Esquema de respuesta de marca"""

    id: UUID
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class RecomendacionIAResponse(BaseModel):
    """Esquema de respuesta de recomendación IA"""

    id: UUID
    usuario_id: UUID
    producto_id: UUID
    score: Optional[Decimal] = None
    razon_recomendacion: Optional[str] = None
    fecha_generacion: datetime

    model_config = ConfigDict(from_attributes=True)


"""
   AUTH SCHEMAS
"""


class UserLogin(BaseModel):
    """Esquema para login"""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Esquema de respuesta de token"""

    access_token: str
    token_type: str = "bearer"
    user: UsuarioResponse


class TokenData(BaseModel):
    """Datos extraídos del token JWT"""

    user_id: Optional[UUID] = None
    email: Optional[str] = None


"""
    CATALOG SCHEMA
"""


class CatalogoHomeResponse(BaseModel):
    destacados: List[ProductoResponse]
    nuevos: List[ProductoResponse]
    ofertas: List[ProductoResponse]
    categorias: List[CategoriaResponse]
    marcas: List[MarcaResponse]


class InventarioProductoResponse(BaseModel):
    """Inventario con relaciones para mostrar en detalle de producto"""

    id: UUID
    producto_id: UUID
    talla_id: UUID
    color_id: UUID
    stock: int
    stock_reservado: int
    talla: Optional[TallaResponse] = None
    color: Optional[ColorResponse] = None
    producto: Optional[ProductoResponse] = None
    model_config = ConfigDict(from_attributes=True)


class AnalisisMorfologicoBase(BaseModel):
    """Base para análisis morfológico"""

    tipo_cuerpo_detectado: str = Field(
        ..., description="Tipo de cuerpo detectado por IA"
    )
    confianza: Optional[Decimal] = Field(
        None, ge=0, le=1, description="Nivel de confianza del modelo (0.0 - 1.0)"
    )

    @field_validator("tipo_cuerpo_detectado")
    def validar_tipo(cls, v):
        return validar_tipo_cuerpo(v)


class AnalisisMorfologicoCreate(AnalisisMorfologicoBase):
    """Schema para crear análisis"""

    # No necesita usuario_id, se toma del token
    pass


class AnalisisMorfologicoResponse(AnalisisMorfologicoBase):
    """Schema de respuesta de análisis"""

    id: UUID
    usuario_id: UUID
    fecha_analisis: datetime

    class Config:
        from_attributes = True


class ReglasRecomendacionBase(BaseModel):
    """Base para reglas de recomendación"""

    tipo_cuerpo: str
    categoria_id: UUID
    prioridad: int = Field(..., ge=1, le=3, description="1=Alta, 2=Media, 3=Baja")
    razon: str = Field(..., min_length=10, max_length=500)
    evitar: bool = False
    activo: bool = True

    @field_validator("tipo_cuerpo")
    def validar_tipo(cls, v):
        return validar_tipo_cuerpo(v)


class ReglasRecomendacionCreate(ReglasRecomendacionBase):
    """Schema para crear regla"""

    pass


class ReglasRecomendacionUpdate(BaseModel):
    """Schema para actualizar regla"""

    prioridad: Optional[int] = Field(None, ge=1, le=3)
    razon: Optional[str] = Field(None, min_length=10, max_length=500)
    evitar: Optional[bool] = None
    activo: Optional[bool] = None


class ReglasRecomendacionResponse(ReglasRecomendacionBase):
    """Schema de respuesta de regla"""

    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class RecomendacionGeneradaBase(BaseModel):
    """Base para recomendación generada"""

    analisis_id: UUID
    producto_id: UUID
    razon_ia: Optional[str] = None
    palabras_clave: Optional[List[str]] = []
    score: Optional[int] = None
    posicion: Optional[int] = Field(None, ge=1, le=10)


class RecomendacionGeneradaCreate(RecomendacionGeneradaBase):
    """Schema para crear recomendación"""

    pass


class RecomendacionGeneradaResponse(RecomendacionGeneradaBase):
    """Schema de respuesta de recomendación"""

    id: UUID
    fue_clickeado: bool
    fue_agregado_carrito: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class ProductoRecomendado(BaseModel):
    """Producto con su recomendación IA"""

    id: UUID
    nombre: str
    descripcion: Optional[str]
    precio_regular: Decimal
    precio_descuento: Optional[Decimal]
    categoria: str
    imagen_principal: Optional[str]
    razon: str  # Explicación de IA
    palabras_clave: List[str] = []
    score: Optional[int] = None


class AnalisisCompletoResponse(BaseModel):
    """Respuesta completa de análisis con recomendaciones"""

    analisis_id: UUID
    tipo_cuerpo: str
    confianza: Optional[Decimal]
    fecha_analisis: datetime
    recomendaciones: List[ProductoRecomendado]
    total_recomendaciones: int

    class Config:
        from_attributes = True


class RegistrarInteraccionRequest(BaseModel):
    """Schema para registrar interacción del usuario"""

    recomendacion_id: UUID
    tipo_interaccion: str = Field(
        ...,
        pattern="^(click|agregar_carrito|compra)$",
        description="Tipo de interacción: click, agregar_carrito, compra",
    )
