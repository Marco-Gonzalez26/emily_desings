from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.utils.auth_dependencies import get_current_user
from app.db.config import get_db
from app.models.models import Usuario
from app.schemas.schemas import (
    InventarioProductoResponse,
    InventarioCreate,
    InventarioUpdate,
    InventarioResponse,
    InventarioAjuste,
)
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


@router.get(
    "/producto/{producto_id}/all", response_model=List[InventarioProductoResponse]
)
def get_all_inventario_producto(
    producto_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener TODO el inventario de un producto, incluye stock 0 (solo admin)"""
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción",
        )

    return inventario_service.get_all_inventario_by_producto(db, producto_id)


@router.get("")
def get_inventario_list(
    skip: int = 0,
    limit: int = 100,
    producto_id: Optional[UUID] = None,
    talla_id: Optional[UUID] = None,
    color_id: Optional[UUID] = None,
    stock_bajo: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar inventario con filtros (solo admin)"""
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción",
        )

    inventarios, total = inventario_service.get_inventario_list(
        db=db,
        skip=skip,
        limit=limit,
        producto_id=producto_id,
        talla_id=talla_id,
        color_id=color_id,
        stock_bajo=stock_bajo,
    )

    return {"inventarios": inventarios, "total": total, "skip": skip, "limit": limit}


@router.get("/stock-bajo")
def get_stock_bajo(
    umbral: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener productos con stock bajo (solo admin)"""
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción",
        )

    return {
        "productos": inventario_service.get_productos_stock_bajo(db, umbral),
        "umbral": umbral,
    }


@router.post("", response_model=InventarioResponse, status_code=status.HTTP_201_CREATED)
def create_inventario(
    inventario_data: InventarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crear nuevo registro de inventario (solo admin)"""
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción",
        )

    return inventario_service.create_inventario(db, inventario_data)


@router.put("/{inventario_id}", response_model=InventarioResponse)
def update_inventario(
    inventario_id: UUID,
    inventario_data: InventarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualizar stock o stock_reservado (solo admin)"""
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción",
        )

    return inventario_service.update_inventario(db, inventario_id, inventario_data)


@router.post("/{inventario_id}/ajustar", response_model=InventarioResponse)
def ajustar_stock(
    inventario_id: UUID,
    ajuste_data: InventarioAjuste,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Ajustar stock (incrementar o decrementar) (solo admin)"""
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción",
        )

    return inventario_service.ajustar_stock(db, inventario_id, ajuste_data)


@router.delete("/{inventario_id}", response_model=InventarioResponse)
def delete_inventario(
    inventario_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminar registro de inventario (solo admin)"""
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción",
        )

    return inventario_service.delete_inventario(db, inventario_id)


@router.get("/producto/{producto_id}/analisis-morfologico")
def get_inventario_quick_add(producto_id: UUID, db: Session = Depends(get_db)):
    """Obtener inventario formateado para el componente QuickAdd modal de analisis"""

    inventarios = inventario_service.get_inventario_by_producto(db, producto_id)

    tallas_map = {}
    colores_map = {}

    for inv in inventarios:
        stock_disponible = inv.stock - inv.stock_reservado

        if inv.talla_id not in tallas_map:
            tallas_map[inv.talla_id] = {
                "id": str(inv.talla_id),
                "nombre": inv.talla.nombre,
                "stock": 0,
            }
        tallas_map[inv.talla_id]["stock"] += stock_disponible

        if inv.color_id not in colores_map:
            colores_map[inv.color_id] = {
                "id": str(inv.color_id),
                "nombre": inv.color.nombre,
                "codigo_hex": inv.color.codigo_hexadecimal,
            }

    return {
        "tallas_disponibles": list(tallas_map.values()),
        "colores_disponibles": list(colores_map.values()),
    }
