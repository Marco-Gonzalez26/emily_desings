from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import uuid4, UUID
from decimal import Decimal
from typing import List

from app.models.models import Orden, OrdenItem, Producto, Usuario

from app.enums.order import OrdenEstado


def create_orden(db: Session, orden_data, user: Usuario) -> Orden:
    if not orden_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La orden debe tener al menos un producto",
        )

    subtotal = Decimal("0.00")
    items_db: List[OrdenItem] = []

    for item in orden_data.items:
        producto = (
            db.query(Producto)
            .filter(Producto.id == item.producto_id, Producto.activo == True)
            .first()
        )

        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {item.producto_id} no encontrado",
            )

        precio_unitario = (
            producto.precio_descuento
            if producto.precio_descuento
            else producto.precio_regular
        )

        subtotal_item = precio_unitario * item.cantidad
        subtotal += subtotal_item

        items_db.append(
            OrdenItem(
                producto_id=producto.id,
                nombre_producto=producto.nombre,
                talla_id=item.talla_id,
                color_id=item.color_id,
                cantidad=item.cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal_item,
            )
        )

    orden = Orden(
        usuario_id=user.id,
        numero_orden=f"ORD-{uuid4().hex[:8].upper()}",
        direccion_envio=orden_data.direccion_envio,
        metodo_pago=orden_data.metodo_pago,
        subtotal=subtotal,
        costo_envio=Decimal("0.00"),
        impuestos=Decimal("0.00"),
        total=subtotal,
        estado=OrdenEstado["PENDIENTE"],
        items=items_db,
    )

    db.add(orden)
    db.commit()
    db.refresh(orden)

    return orden


def get_mis_ordenes(db: Session, user: Usuario) -> List[Orden]:
    return (
        db.query(Orden)
        .filter(Orden.usuario_id == user.id)
        .order_by(Orden.fecha_orden.desc())
        .all()
    )


def get_orden_by_id(db: Session, orden_id: UUID, user: Usuario) -> Orden:
    orden = (
        db.query(Orden)
        .filter(Orden.id == orden_id, Orden.usuario_id == user.id)
        .first()
    )

    if not orden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada",
        )

    return orden
