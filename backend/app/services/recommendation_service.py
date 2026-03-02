from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from uuid import UUID
import random

from app.models.models import ReglasRecomendacion, AnalisisMorfologico
from app.models.models import Producto, Categoria


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

    # 1. Obtener categorías recomendadas para este tipo de cuerpo
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

    # 2. Obtener historial del usuario (productos ya recomendados)
    productos_ya_vistos = _obtener_productos_ya_vistos(db, usuario_id)

    productos_finales = []

    for regla in reglas:
        # 3. Query de productos de esta categoría
        query = (
            db.query(Producto)
            .join(Categoria)
            .filter(
                Producto.categoria_id == regla.categoria_id,
                Producto.activo == True,
            )
        )

        # 4. EXCLUIR productos ya vistos
        if productos_ya_vistos:
            query = query.filter(~Producto.id.in_(productos_ya_vistos))

        productos = query.all()

        # 5. Aplicar scoring inteligente
        productos_scored = []
        for p in productos:
            score = _calcular_score_producto(p, regla)
            productos_scored.append((p, score))

        # Ordenar por score y tomar los mejores de esta categoría
        productos_scored.sort(key=lambda x: x[1], reverse=True)

        # Tomar 2-3 productos por categoría según prioridad
        cantidad = 3 if regla.prioridad == 1 else 2
        productos_finales.extend([p for p, _ in productos_scored[:cantidad]])

        if len(productos_finales) >= limite:
            break

    # 6. Shuffle final para variedad
    random.shuffle(productos_finales)

    # 7. Convertir a diccionarios con información completa
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

    # Factor 1: Prioridad de la regla (más importante)
    score += (4 - regla.prioridad) * 30  # Prioridad 1 = +90, Prioridad 3 = +30

    # Factor 2: Popularidad (productos destacados)
    if producto.es_destacado:
        score += 25

    # Factor 3: Novedad (productos nuevos)
    if producto.es_nuevo:
        score += 20

    # Factor 4: Tiene stock disponible
    stock_total = sum(inv.stock for inv in producto.inventarios)
    if stock_total > 0:
        score += 15
        if stock_total > 10:
            score += 10  # Bonus por buen stock

    # Factor 5: Precio (preferir rango medio accesible)
    precio = float(producto.precio_descuento or producto.precio_regular)
    if 30 <= precio <= 80:  # Rango accesible
        score += 10

    # Factor 6: Tiene descuento (ofertas)
    if producto.es_oferta and producto.precio_descuento:
        score += 15

    # Factor 7: Aleatoriedad (para variedad)
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
