from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from uuid import uuid4, UUID
from decimal import Decimal
from typing import List
from datetime import datetime
import stripe
import os

from app.models.models import (
    Orden,
    OrdenItem,
    Producto,
    Usuario,
    Carrito,
    Inventario,
    CarritoItem,
)
from app.schemas.schemas import OrdenCreate
from app.enums.order import OrdenEstado

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_orden(db: Session, orden_data: OrdenCreate, user: Usuario) -> Orden:
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
                producto_id=item.producto_id,
                nombre_producto=item.nombre_producto,
                talla_id=item.talla_id,
                color_id=item.color_id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                subtotal=item.subtotal,
            )
        )

    orden = Orden(
        usuario_id=user.id,
        numero_orden=f"ORD-{uuid4().hex[:8].upper()}",
        direccion_envio=orden_data.direccion_envio,
        metodo_pago=orden_data.metodo_pago,
        subtotal=orden_data.subtotal,
        costo_envio=orden_data.costo_envio,
        impuestos=orden_data.impuestos,
        total=orden_data.total,
        estado=OrdenEstado["PENDIENTE"],
        items=items_db,
    )

    db.add(orden)
    db.commit()
    db.refresh(orden)

    return orden


def get_mis_ordenes(
    db: Session, user: Usuario, skip: int = 0, limit: int = 10
) -> tuple[List[Orden], int]:
    query = db.query(Orden).filter(Orden.usuario_id == user.id)
    total = query.count()
    ordenes = query.order_by(Orden.fecha_orden.desc()).offset(skip).limit(limit).all()
    return ordenes, total


def get_orden_by_id(db: Session, orden_id: UUID, user: Usuario) -> Orden:
    orden = (
        db.query(Orden)
        .options(joinedload(Orden.items))
        .filter(Orden.id == orden_id, Orden.usuario_id == user.id)
        .first()
    )

    if not orden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada",
        )

    return orden


def crear_stripe_checkout_session(
    db: Session, orden_id: UUID, user: Usuario, success_url: str, cancel_url: str
) -> dict:
    """Crear sesión de Stripe Checkout para una orden"""

    orden = (
        db.query(Orden)
        .options(joinedload(Orden.items))
        .filter(Orden.id == orden_id, Orden.usuario_id == user.id)
        .first()
    )

    if not orden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada"
        )

    if orden.estado != OrdenEstado["PENDIENTE"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La orden ya ha sido procesada",
        )

    # Crear line items para Stripe
    line_items = []
    for item in orden.items:
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.nombre_producto,
                    },
                    "unit_amount": int(float(item.precio_unitario) * 100),
                },
                "quantity": item.cantidad,
            }
        )

    # Agregar envío si aplica
    if float(orden.costo_envio) > 0:
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Envío",
                    },
                    "unit_amount": int(float(orden.costo_envio) * 100),
                },
                "quantity": 1,
            }
        )

    # Agregar impuestos si aplica
    if float(orden.impuestos) > 0:
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Impuestos (12%)",
                    },
                    "unit_amount": int(float(orden.impuestos) * 100),
                },
                "quantity": 1,
            }
        )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=success_url
            + f"?session_id={{CHECKOUT_SESSION_ID}}&orden_id={orden_id}",
            cancel_url=cancel_url,
            metadata={
                "orden_id": str(orden_id),
                "numero_orden": orden.numero_orden,
                "usuario_id": str(user.id),
            },
        )

        return {
            "checkout_url": session.url,
            "session_id": session.id,
        }

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear sesión de pago: {str(e)}",
        )


def confirmar_pago_stripe(db: Session, session_id: str, user: Usuario) -> Orden:
    """Confirmar el pago, actualizar orden y descontar stock"""

    try:
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status != "paid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pago no ha sido completado",
            )

        orden_id = UUID(session.metadata.get("orden_id"))
        orden = (
            db.query(Orden)
            .options(joinedload(Orden.items))
            .filter(Orden.id == orden_id, Orden.usuario_id == user.id)
            .first()
        )

        if not orden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada"
            )

        # Descontar stock de inventario
        for item in orden.items:
            inventario = (
                db.query(Inventario)
                .filter(
                    Inventario.producto_id == item.producto_id,
                    Inventario.talla_id == item.talla_id,
                    Inventario.color_id == item.color_id,
                )
                .first()
            )

            if inventario:
                inventario.stock -= item.cantidad
                # Liberar reserva solo si existe y no excede
                if inventario.stock_reservado >= item.cantidad:
                    inventario.stock_reservado -= item.cantidad
                else:
                    # Si no hay suficiente reservado, dejar en 0
                    inventario.stock_reservado = 0

        orden.estado = OrdenEstado["CONFIRMADO"]
        orden.stripe_payment_id = session.payment_intent
        orden.fecha_actualizacion_estado = datetime.now()

        # Vaciar carrito y liberar reservas restantes
        carrito = (
            db.query(Carrito)
            .filter(Carrito.usuario_id == user.id, Carrito.activo == True)
            .first()
        )

        if carrito:
            # Liberar reservas de items que aún estén en el carrito
            items_carrito = (
                db.query(CarritoItem).filter(CarritoItem.carrito_id == carrito.id).all()
            )

            for item in items_carrito:
                inv = (
                    db.query(Inventario)
                    .filter(
                        Inventario.producto_id == item.producto_id,
                        Inventario.talla_id == item.talla_id,
                        Inventario.color_id == item.color_id,
                    )
                    .first()
                )
                if inv and inv.stock_reservado >= item.cantidad:
                    inv.stock_reservado -= item.cantidad

            # Eliminar items del carrito
            db.query(CarritoItem).filter(CarritoItem.carrito_id == carrito.id).delete()

            # Eliminar el carrito
            db.delete(carrito)

        # Un solo commit al final
        db.commit()
        db.refresh(orden)

        return orden

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al confirmar pago: {str(e)}",
        )
