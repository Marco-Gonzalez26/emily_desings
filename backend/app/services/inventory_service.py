from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from typing import List

from app.models.models import Inventario


def get_inventario_by_producto(db: Session, producto_id: UUID) -> List[Inventario]:
    """Obtener inventario disponible de un producto con stock > 0"""
    inventory = (
        db.query(Inventario)
        .options(joinedload(Inventario.talla), joinedload(Inventario.color))
        .filter(Inventario.producto_id == producto_id, Inventario.stock > 0)
        .all()
    )
    print(inventory)
    return (
        db.query(Inventario)
        .options(joinedload(Inventario.talla), joinedload(Inventario.color))
        .filter(
            Inventario.producto_id == producto_id,
            Inventario.stock > Inventario.stock_reservado,
        )
        .all()
    )


def get_stock_disponible(
    db: Session, producto_id: UUID, talla_id: UUID, color_id: UUID
) -> int:
    """Obtener stock disponible de una combinación específica"""
    inventario = (
        db.query(Inventario)
        .filter(
            Inventario.producto_id == producto_id,
            Inventario.talla_id == talla_id,
            Inventario.color_id == color_id,
        )
        .first()
    )

    if not inventario:
        return 0

    return inventario.stock - inventario.stock_reservado
