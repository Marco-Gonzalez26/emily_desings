from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from fastapi.responses import StreamingResponse
from app.services.pdf_service import generar_pdf_orden
from app.db.config import get_db
from app.utils.auth_dependencies import get_current_user
from app.models.models import Usuario
from app.schemas.schemas import (
    OrdenCreate,
    OrdenResponse,
    StripeCheckoutRequest,
    StripeCheckoutResponse,
)
from app.services import order_service

router = APIRouter(prefix="/api/ordenes", tags=["Órdenes"])


@router.post("/", response_model=OrdenResponse, status_code=status.HTTP_201_CREATED)
def crear_orden(
    orden_data: OrdenCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crear una nueva orden"""
    return order_service.create_orden(db, orden_data, current_user)


@router.post("/{orden_id}/checkout", response_model=StripeCheckoutResponse)
def crear_checkout_session(
    orden_id: UUID,
    data: StripeCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crear sesión de Stripe Checkout para una orden"""
    return order_service.crear_stripe_checkout_session(
        db, orden_id, current_user, data.success_url, data.cancel_url
    )


@router.post("/confirmar-pago/{session_id}", response_model=OrdenResponse)
def confirmar_pago(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Confirmar pago de Stripe y actualizar orden"""
    return order_service.confirmar_pago_stripe(db, session_id, current_user)


@router.get("/mias", response_model=List[OrdenResponse])
def mis_ordenes(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener mis órdenes"""
    ordenes, total = order_service.get_mis_ordenes(db, current_user, skip, limit)
    return ordenes


@router.get("/{orden_id}", response_model=OrdenResponse)
def detalle_orden(
    orden_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener detalle de una orden"""
    return order_service.get_orden_by_id(db, orden_id, current_user)


@router.get("/{orden_id}/pdf")
def descargar_pdf_orden(
    orden_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Descargar PDF de la orden"""
    orden = order_service.get_orden_by_id(db, orden_id, current_user)

    pdf_buffer = generar_pdf_orden(orden)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=orden_{orden.numero_orden}.pdf"
        },
    )
