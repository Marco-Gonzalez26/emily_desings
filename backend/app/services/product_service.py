"""
Servicio de productos
Maneja la lógica de negocio para CRUD de productos
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from uuid import UUID
from typing import List, Optional
from decimal import Decimal

from app.models.models import Producto, Usuario, ImagenProducto
from app.schemas.schemas import ProductoCreate, ProductoUpdate


def get_producto_by_id(db: Session, producto_id: UUID) -> Producto:
    """
    Obtener producto por ID

    Args:
        db: Sesión de base de datos
        producto_id: UUID del producto

    Returns:
        Producto encontrado

    Raises:
        HTTPException: Si el producto no existe
    """
    producto = db.query(Producto).filter(Producto.id == producto_id).first()

    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {producto_id} no encontrado",
        )

    return producto


def get_producto_by_sku(db: Session, sku: str) -> Optional[Producto]:
    """Obtener producto por SKU"""
    return db.query(Producto).filter(Producto.sku == sku).first()


def get_productos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    categoria_id: Optional[UUID] = None,
    marca_id: Optional[UUID] = None,
    precio_min: Optional[Decimal] = None,
    precio_max: Optional[Decimal] = None,
    es_nuevo: Optional[bool] = None,
    es_oferta: Optional[bool] = None,
    es_destacado: Optional[bool] = None,
    activo: Optional[bool] = True,
    search: Optional[str] = None,
) -> tuple[List[Producto], int]:
    """
    Listar productos con filtros y paginación

    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        categoria_id: Filtrar por categoría
        marca_id: Filtrar por marca
        precio_min: Precio mínimo
        precio_max: Precio máximo
        es_nuevo: Filtrar productos nuevos
        es_oferta: Filtrar productos en oferta
        es_destacado: Filtrar productos destacados
        activo: Filtrar productos activos/inactivos
        search: Buscar en nombre o descripción

    Returns:
        Tupla con (lista de productos, total de registros)
    """
    query = db.query(Producto)

    # Aplicar filtros
    if activo is not None:
        query = query.filter(Producto.activo == activo)

    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)

    if marca_id:
        query = query.filter(Producto.marca_id == marca_id)

    if precio_min is not None:
        query = query.filter(Producto.precio_regular >= precio_min)

    if precio_max is not None:
        query = query.filter(Producto.precio_regular <= precio_max)

    if es_nuevo is not None:
        query = query.filter(Producto.es_nuevo == es_nuevo)

    if es_oferta is not None:
        query = query.filter(Producto.es_oferta == es_oferta)

    if es_destacado is not None:
        query = query.filter(Producto.es_destacado == es_destacado)

    if search:
        search_filter = or_(
            Producto.nombre.ilike(f"%{search}%"),
            Producto.descripcion.ilike(f"%{search}%"),
            Producto.sku.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    # Contar total
    total = query.count()

    # Aplicar paginación
    productos = query.offset(skip).limit(limit).all()

    return productos, total


def create_producto(
    db: Session, producto_data: ProductoCreate, admin_user: Usuario
) -> Producto:
    """
    Crear un nuevo producto

    Args:
        db: Sesión de base de datos
        producto_data: Datos del producto
        admin_user: Usuario administrador que crea el producto

    Returns:
        Producto creado

    Raises:
        HTTPException: Si el SKU ya existe
    """
    # Verificar que el SKU no exista
    existing_producto = get_producto_by_sku(db, producto_data.sku)
    if existing_producto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto con el SKU '{producto_data.sku}'",
        )

    # Validar que precio_descuento sea menor que precio_regular
    if (
        producto_data.precio_descuento
        and producto_data.precio_descuento >= producto_data.precio_regular
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El precio de descuento debe ser menor al precio regular",
        )
    print(producto_data.nombre)
    print(producto_data.descripcion)
    print(producto_data.precio_descuento)
    print(producto_data.precio_regular)
    print(producto_data.marca_id)
    print(producto_data.categoria_id)
    print(producto_data.es_nuevo)
    print(producto_data.es_oferta)
    print(producto_data.es_destacado)
    print(producto_data.activo)

    # Crear producto
    new_producto = Producto(
        **producto_data.model_dump(), administrador_id=admin_user.id
    )

    db.add(new_producto)
    db.commit()
    db.refresh(new_producto)

    return new_producto


def update_producto(
    db: Session, producto_id: UUID, producto_data: ProductoUpdate, admin_user: Usuario
) -> Producto:
    """
    Actualizar un producto existente

    Args:
        db: Sesión de base de datos
        producto_id: UUID del producto a actualizar
        producto_data: Datos a actualizar
        admin_user: Usuario administrador que actualiza

    Returns:
        Producto actualizado

    Raises:
        HTTPException: Si el producto no existe o el SKU está duplicado
    """
    # Obtener producto
    producto = get_producto_by_id(db, producto_id)

    # Obtener solo los campos que vienen en la petición
    update_data = producto_data.model_dump(exclude_unset=True)

    # Si se actualiza el SKU, verificar que no exista
    if "sku" in update_data and update_data["sku"] != producto.sku:
        existing_producto = get_producto_by_sku(db, update_data["sku"])
        if existing_producto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un producto con el SKU '{update_data['sku']}'",
            )

    # Validar precios si se actualizan
    precio_regular = update_data.get("precio_regular", producto.precio_regular)
    precio_descuento = update_data.get("precio_descuento", producto.precio_descuento)

    if precio_descuento and precio_descuento >= precio_regular:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El precio de descuento debe ser menor al precio regular",
        )

    # Actualizar campos
    for field, value in update_data.items():
        setattr(producto, field, value)

    db.commit()
    db.refresh(producto)

    return producto


def delete_producto(
    db: Session, producto_id: UUID, admin_user: Usuario, soft_delete: bool = True
) -> Producto:
    """
    Eliminar un producto (soft delete por defecto)

    Args:
        db: Sesión de base de datos
        producto_id: UUID del producto a eliminar
        admin_user: Usuario administrador
        soft_delete: Si es True, solo marca como inactivo. Si es False, elimina físicamente.

    Returns:
        Producto eliminado/desactivado

    Raises:
        HTTPException: Si el producto no existe
    """
    producto = get_producto_by_id(db, producto_id)

    if soft_delete:
        # Soft delete - solo marcar como inactivo
        producto.activo = False
        db.commit()
        db.refresh(producto)
        return producto
    else:
        # Hard delete - eliminar físicamente
        db.delete(producto)
        db.commit()
        return producto


def get_productos_destacados(db: Session, limit: int = 10) -> List[Producto]:
    """Obtener productos destacados"""
    return (
        db.query(Producto)
        .filter(Producto.es_destacado == True, Producto.activo == True)
        .limit(limit)
        .all()
    )


def get_productos_nuevos(db: Session, limit: int = 10) -> List[Producto]:
    """Obtener productos nuevos"""
    return (
        db.query(Producto)
        .filter(Producto.es_nuevo == True, Producto.activo == True)
        .order_by(Producto.fecha_creacion.desc())
        .limit(limit)
        .all()
    )


def get_productos_en_oferta(db: Session, limit: int = 10) -> List[Producto]:
    """Obtener productos en oferta"""
    return (
        db.query(Producto)
        .filter(
            Producto.es_oferta == True,
            Producto.activo == True,
            Producto.precio_descuento.isnot(None),
        )
        .limit(limit)
        .all()
    )
