from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.config import get_db
from app.schemas.schemas import InventarioProductoResponse
import app.services.inventory_service as inventario_service

router = APIRouter(prefix="/api/inventario", tags=["Inventario"])


@router.get("/producto/{producto_id}", response_model=List[InventarioProductoResponse])
def get_inventario_producto(producto_id: UUID, db: Session = Depends(get_db)):
    """Obtener inventario disponible de un producto (solo con stock)"""
    return inventario_service.get_inventario_by_producto(db, producto_id)


@router.get("/disponible/{producto_id}/{talla_id}/{color_id}")
def get_stock_disponible(
    producto_id: UUID, talla_id: UUID, color_id: UUID, db: Session = Depends(get_db)
):
    """Verificar stock disponible de una combinación específica"""
    stock = inventario_service.get_stock_disponible(db, producto_id, talla_id, color_id)
    return {"stock_disponible": stock}
