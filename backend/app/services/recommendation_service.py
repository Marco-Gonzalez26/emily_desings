from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from uuid import UUID
import random

from app.models.models import ReglasRecomendacion, AnalisisMorfologico
from app.models.models import Producto, Categoria, Inventario


def generar_recomendaciones_inteligentes(
    db: Session, tipo_cuerpo: str, usuario_id: UUID, limite: int = 10
) -> List[Dict]:
    """
    Genera recomendaciones personalizadas y variadas usando algoritmo de scoring

    Args:
        db: Sesión de base de datos
        tipo_cuerpo: Tipo de cuerpo detectado (ej: "Triangulo Invertido")
        usuario_id: ID del usuario
        limite: Número máximo de productos a recomendar

    Returns:
        Lista de productos recomendados con información completa
    """

    # Obtener categorías recomendadas para este tipo de cuerpo
    reglas = (
        db.query(ReglasRecomendacion)
        .filter(
            ReglasRecomendacion.tipo_cuerpo == tipo_cuerpo,
            ReglasRecomendacion.evitar == False,
            ReglasRecomendacion.activo == True,
        )
        .order_by(ReglasRecomendacion.prioridad)
        .all()
    )

    if not reglas:
        print(f"No hay reglas para tipo de cuerpo: {tipo_cuerpo}")
        return []

    # Obtener historial del usuario
    productos_ya_vistos = _obtener_productos_ya_vistos(db, usuario_id)

    productos_finales = []

    for regla in reglas:
        # Productos de esta categoría
        query = (
            db.query(Producto)
            .join(Categoria)
            .join(Inventario)
            .filter(
                Producto.categoria_id == regla.categoria_id,
                Producto.activo == True,
                Inventario.stock > Inventario.stock_reservado,
            )
            .distinct()
        )

        if productos_ya_vistos:
            query = query.filter(~Producto.id.in_(productos_ya_vistos))

        productos = query.all()

        # Aplicar scoring
        productos_scored = []
        for p in productos:
            score = _calcular_score_producto(p, regla)
            productos_scored.append((p, score))

        # Ordenar por score y tomar los mejores de esta categoría
        productos_scored.sort(key=lambda x: x[1], reverse=True)

        # Tomar 1 producto por categoria
        cantidad = 1
        productos_finales.extend([p for p, _ in productos_scored[:cantidad]])

        if len(productos_finales) >= limite:
            break

    # Shuffle para variedad
    random.shuffle(productos_finales)
    return [_producto_a_dict(p) for p in productos_finales[:limite]]


def _obtener_productos_ya_vistos(db: Session, usuario_id: UUID) -> set:
    """Obtiene IDs de productos ya recomendados al usuario"""
    analisis_previos = (
        db.query(AnalisisMorfologico)
        .filter(AnalisisMorfologico.usuario_id == usuario_id)
        .order_by(AnalisisMorfologico.fecha_analisis.desc())
        .limit(5)
        .all()
    )

    productos_vistos = set()

    for analisis in analisis_previos:
        for rec in analisis.recomendaciones:
            productos_vistos.add(rec.producto_id)

    return productos_vistos


def _calcular_score_producto(producto: Producto, regla: ReglasRecomendacion) -> int:
    """
    Calcula score de un producto basado en múltiples factores
    Mayor score = mejor match
    """
    score = 0
    score += (4 - regla.prioridad) * 30
    if producto.es_destacado:
        score += 25
    if producto.es_nuevo:
        score += 20
    stock_total = sum(inv.stock for inv in producto.inventarios)

    stock_disponible = sum(
        inv.stock - inv.stock_reservado for inv in producto.inventarios
    )

    if stock_disponible > 0:
        score += 15
        if stock_disponible > 10:
            score += 10

    precio = float(producto.precio_descuento or producto.precio_regular)
    if 30 <= precio <= 80:
        score += 10
    if producto.es_oferta and producto.precio_descuento:
        score += 15
    score += random.randint(0, 20)

    return score


def _producto_a_dict(producto: Producto) -> Dict:
    """Convierte producto SQLAlchemy a diccionario"""
    # Obtener imagen principal
    imagen_principal = None
    if producto.imagenes:
        img_principal = next(
            (img for img in producto.imagenes if img.es_principal), None
        )
        imagen_principal = (
            img_principal.url_imagen
            if img_principal
            else producto.imagenes[0].url_imagen
        )
    stock_disponible = sum(
        inv.stock - inv.stock_reservado for inv in producto.inventarios
    )
    return {
        "id": str(producto.id),
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio": float(producto.precio_descuento or producto.precio_regular),
        "precio_regular": float(producto.precio_regular),
        "precio_descuento": (
            float(producto.precio_descuento) if producto.precio_descuento else None
        ),
        "categoria": producto.categoria.nombre if producto.categoria else None,
        "imagen_principal": imagen_principal,
        "es_oferta": producto.es_oferta,
        "es_nuevo": producto.es_nuevo,
        "es_destacado": producto.es_destacado,
        "stock_disponible": stock_disponible,
    }


def obtener_reglas_por_tipo(db: Session, tipo_cuerpo: str) -> List[Dict]:
    """
    Obtiene las reglas de recomendación para un tipo de cuerpo
    Útil para debugging o mostrar al usuario
    """
    reglas = (
        db.query(ReglasRecomendacion)
        .join(Categoria)
        .filter(
            ReglasRecomendacion.tipo_cuerpo == tipo_cuerpo,
            ReglasRecomendacion.activo == True,
        )
        .order_by(ReglasRecomendacion.prioridad)
        .all()
    )

    return [
        {
            "categoria": regla.categoria.nombre,
            "prioridad": regla.prioridad,
            "razon": regla.razon,
            "evitar": regla.evitar,
        }
        for regla in reglas
    ]
