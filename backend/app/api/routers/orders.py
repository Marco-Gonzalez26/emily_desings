from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.db.config import get_db
from app.utils.auth_dependencies import get_current_user
from app.models.models import Usuario
from app.schemas.schemas import OrdenCreate, OrdenResponse
from app.services import order_service

router = APIRouter(prefix="/api/ordenes", tags=["Órdenes"])


@router.post("/", response_model=OrdenResponse, status_code=status.HTTP_201_CREATED)
def crear_orden(
    orden_data: OrdenCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return order_service.create_orden(db, orden_data, current_user)


@router.get("/mias", response_model=List[OrdenResponse])
def mis_ordenes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return order_service.get_mis_ordenes(db, current_user)


@router.get("/{orden_id}", response_model=OrdenResponse)
def detalle_orden(
    orden_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return order_service.get_orden_by_id(db, orden_id, current_user)
