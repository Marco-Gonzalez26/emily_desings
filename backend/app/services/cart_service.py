from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from uuid import UUID

from app.models.models import Carrito, CarritoItem, Producto


def get_or_create_carrito(db: Session, usuario_id: UUID) -> Carrito:
    """Obtener carrito activo del usuario o crear uno nuevo"""
    carrito = (
        db.query(Carrito)
        .options(
            joinedload(Carrito.items)
            .joinedload(CarritoItem.producto)
            .joinedload(Producto.imagenes),
            joinedload(Carrito.items).joinedload(CarritoItem.talla),
            joinedload(Carrito.items).joinedload(CarritoItem.color),
        )
        .filter(Carrito.usuario_id == usuario_id, Carrito.activo == True)
        .first()
    )

    if not carrito:
        carrito = Carrito(usuario_id=usuario_id, activo=True)
        db.add(carrito)
        db.commit()
        db.refresh(carrito)

    return carrito


def add_item(
    db: Session,
    usuario_id: UUID,
    producto_id: UUID,
    talla_id: UUID,
    color_id: UUID,
    cantidad: int,
) -> Carrito:
    """Agregar item al carrito o aumentar cantidad si ya existe"""
    # Verificar que el producto existe y está activo
    producto = (
        db.query(Producto)
        .filter(Producto.id == producto_id, Producto.activo == True)
        .first()
    )

    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )

    carrito = get_or_create_carrito(db, usuario_id)

    # Verificar si el item ya existe (mismo producto, talla y color)
    existing_item = (
        db.query(CarritoItem)
        .filter(
            CarritoItem.carrito_id == carrito.id,
            CarritoItem.producto_id == producto_id,
            CarritoItem.talla_id == talla_id,
            CarritoItem.color_id == color_id,
        )
        .first()
    )

    if existing_item:
        # Aumentar cantidad
        existing_item.cantidad += cantidad
        db.commit()
    else:
        # Crear nuevo item
        precio = producto.precio_descuento or producto.precio_regular
        new_item = CarritoItem(
            carrito_id=carrito.id,
            producto_id=producto_id,
            talla_id=talla_id,
            color_id=color_id,
            cantidad=cantidad,
            precio_unitario=precio,
        )
        db.add(new_item)
        db.commit()

    return get_or_create_carrito(db, usuario_id)


def update_item_quantity(
    db: Session,
    usuario_id: UUID,
    item_id: UUID,
    cantidad: int,
) -> Carrito:
    """Actualizar cantidad de un item del carrito"""
    carrito = get_or_create_carrito(db, usuario_id)

    item = (
        db.query(CarritoItem)
        .filter(
            CarritoItem.id == item_id,
            CarritoItem.carrito_id == carrito.id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado en el carrito",
        )

    if cantidad <= 0:
        db.delete(item)
    else:
        item.cantidad = cantidad

    db.commit()
    return get_or_create_carrito(db, usuario_id)


def remove_item(db: Session, usuario_id: UUID, item_id: UUID) -> Carrito:
    """Eliminar un item del carrito"""
    carrito = get_or_create_carrito(db, usuario_id)

    item = (
        db.query(CarritoItem)
        .filter(
            CarritoItem.id == item_id,
            CarritoItem.carrito_id == carrito.id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado en el carrito",
        )

    db.delete(item)
    db.commit()
    return get_or_create_carrito(db, usuario_id)


def clear_carrito(db: Session, usuario_id: UUID) -> Carrito:
    """Vaciar el carrito"""
    carrito = get_or_create_carrito(db, usuario_id)

    db.query(CarritoItem).filter(CarritoItem.carrito_id == carrito.id).delete()

    db.commit()
    return get_or_create_carrito(db, usuario_id)


def get_total(db: Session, usuario_id: UUID) -> dict:
    """Calcular totales del carrito"""
    carrito = get_or_create_carrito(db, usuario_id)

    subtotal = sum(
        float(item.precio_unitario) * item.cantidad for item in carrito.items
    )
    envio = 0.0 if subtotal >= 50 else 5.0
    total = subtotal + envio

    return {
        "subtotal": round(subtotal, 2),
        "envio": envio,
        "total": round(total, 2),
        "cantidad_items": sum(item.cantidad for item in carrito.items),
    }
