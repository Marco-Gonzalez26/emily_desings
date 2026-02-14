"""
Esquemas Pydantic para validación de datos en FastAPI
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class UsuarioBase(BaseModel):
    """Esquema base de usuario"""

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

    sku: str
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
    model_config = ConfigDict(from_attributes=True)


class ProductoDetailResponse(ProductoResponse):
    """Respuesta detallada de producto con más información"""

    administrador_id: Optional[UUID] = None

    # TODO: Agregar más relaciones si se necesita
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
    producto: Optional["ProductoResponse"] = None  # ← Incluir producto
    created_at: datetime

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
    talla_id: UUID
    color_id: UUID
    cantidad: int = Field(..., gt=0)


class OrdenItemResponse(OrdenItemBase):
    """Esquema de respuesta de item de orden"""

    id: UUID

    model_config = ConfigDict(from_attributes=True)


class OrdenCreate(BaseModel):
    """Esquema para crear orden"""

    direccion_envio: str
    metodo_pago: str
    items: List[OrdenItemCreate] = Field(default_factory=list)


class OrdenResponse(BaseModel):
    """Esquema de respuesta de orden"""

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
    fecha_orden: datetime
    items: List[OrdenItemCreate] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


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
