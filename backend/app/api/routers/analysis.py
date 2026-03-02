from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import tempfile
import os
from datetime import datetime

from app.db.config import get_db
from app.models.models import Usuario
from app.models.models import AnalisisMorfologico, RecomendacionGenerada
from app.schemas.schemas import (
    AnalisisCompletoResponse,
    AnalisisMorfologicoResponse,
    ProductoRecomendado,
    RegistrarInteraccionRequest,
)
from app.utils.auth_dependencies import get_current_user
from app.services import recommendation_service, ai_service

router = APIRouter(prefix="/api/analisis", tags=["Análisis Morfológico"])


@router.post("/analizar-imagen", response_model=AnalisisCompletoResponse)
async def analizar_imagen(
    file: UploadFile = File(..., description="Imagen corporal para análisis"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Analiza una imagen corporal y genera recomendaciones personalizadas

    **Flujo:**
    1. Recibe imagen (NO se almacena por protección de datos)
    2. Procesa con modelo IA de clasificación
    3. Elimina imagen inmediatamente
    4. Guarda solo resultado en BD
    5. Genera recomendaciones inteligentes
    6. Usa IA para explicaciones personalizadas

    **Retorna:**
    - Tipo de cuerpo detectado
    - Nivel de confianza
    - 10 productos recomendados con explicaciones IA
    """

    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen (JPG, PNG, etc.)",
        )

    # 1. Guardar temporalmente (se elimina automáticamente)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        contents = await file.read()
        temp_file.write(contents)
        temp_path = temp_file.name

    try:
        # 2. CLASIFICAR CON TU MODELO (Segmentación U2Net + Clasificación)
        from app.services import clasification_service

        print(f"\n{'='*50}")
        print(f"🔬 ANÁLISIS MORFOLÓGICO")
        print(f"{'='*50}")
        print(f"📁 Imagen temporal: {temp_path}")

        resultado = clasification_service.clasificar_tipo_cuerpo(temp_path)

        print(f"\n📊 RESULTADO:")
        print(
            f"   Tipo: {resultado['tipo_cuerpo']} ({resultado['tipo_cuerpo_original']})"
        )
        print(f"   Confianza: {resultado['confianza']:.2%}")
        print(f"{'='*50}\n")

        # 3. ELIMINAR IMAGEN INMEDIATAMENTE (cumplimiento legal)
        os.unlink(temp_path)
        print(f"🗑️  Imagen eliminada por seguridad")

        # 4. Guardar análisis en BD (SIN imagen)
        analisis = AnalisisMorfologico(
            usuario_id=current_user.id,
            tipo_cuerpo_detectado=resultado["tipo_cuerpo"],
            confianza=resultado["confianza"],
            fecha_analisis=datetime.utcnow(),
        )
        db.add(analisis)
        db.commit()
        db.refresh(analisis)
        print(f"💾 Análisis guardado en BD (ID: {analisis.id})")

        # 5. Generar recomendaciones inteligentes
        productos_recomendados = (
            recommendation_service.generar_recomendaciones_inteligentes(
                db=db,
                tipo_cuerpo=resultado["tipo_cuerpo"],
                usuario_id=current_user.id,
                limite=10,
            )
        )

        if not productos_recomendados:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron productos para el tipo de cuerpo: {resultado['tipo_cuerpo']}",
            )

        # 6. Generar explicaciones con IA (gpt-oss-120b)
        productos_con_ia = ai_service.generar_explicaciones_batch(
            tipo_cuerpo=resultado["tipo_cuerpo"],
            productos=productos_recomendados,
            usar_reasoning=True,
        )

        # 7. Guardar recomendaciones en BD (para tracking)
        for idx, prod in enumerate(productos_con_ia, start=1):
            recomendacion = RecomendacionGenerada(
                analisis_id=analisis.id,
                producto_id=UUID(prod["id"]),
                razon_ia=prod.get("razon"),
                palabras_clave=prod.get("palabras_clave", []),
                posicion=idx,
                fue_clickeado=False,
                fue_agregado_carrito=False,
            )
            db.add(recomendacion)

        db.commit()

        # 8. Construir respuesta
        productos_response = [
            ProductoRecomendado(
                id=UUID(p["id"]),
                nombre=p["nombre"],
                descripcion=p.get("descripcion"),
                precio_regular=p["precio_regular"],
                precio_descuento=p.get("precio_descuento"),
                categoria=p["categoria"],
                imagen_principal=p.get("imagen_principal"),
                razon=p.get("razon", ""),
                palabras_clave=p.get("palabras_clave", []),
                score=None,
            )
            for p in productos_con_ia
        ]

        return AnalisisCompletoResponse(
            analisis_id=analisis.id,
            tipo_cuerpo=resultado["tipo_cuerpo"],
            confianza=resultado["confianza"],
            fecha_analisis=analisis.fecha_analisis,
            recomendaciones=productos_response,
            total_recomendaciones=len(productos_response),
        )

    except Exception as e:
        # Asegurar eliminación de imagen incluso si hay error
        if os.path.exists(temp_path):
            os.unlink(temp_path)

        # Re-lanzar excepción
        if isinstance(e, HTTPException):
            raise e

        print(f"❌ Error en análisis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando análisis: {str(e)}",
        )


@router.get("/historial", response_model=List[AnalisisMorfologicoResponse])
def obtener_historial(
    limite: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene el historial de análisis del usuario
    """
    analisis = (
        db.query(AnalisisMorfologico)
        .filter(AnalisisMorfologico.usuario_id == current_user.id)
        .order_by(AnalisisMorfologico.fecha_analisis.desc())
        .limit(limite)
        .all()
    )

    return analisis


@router.get("/historial/{analisis_id}", response_model=AnalisisCompletoResponse)
def obtener_analisis_completo(
    analisis_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene un análisis específico con sus recomendaciones
    """
    analisis = (
        db.query(AnalisisMorfologico)
        .filter(
            AnalisisMorfologico.id == analisis_id,
            AnalisisMorfologico.usuario_id == current_user.id,
        )
        .first()
    )

    if not analisis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Análisis no encontrado"
        )

    # Obtener recomendaciones guardadas
    recomendaciones_db = (
        db.query(RecomendacionGenerada)
        .filter(RecomendacionGenerada.analisis_id == analisis_id)
        .order_by(RecomendacionGenerada.posicion)
        .all()
    )

    productos_response = []
    for rec in recomendaciones_db:
        producto = rec.producto
        productos_response.append(
            ProductoRecomendado(
                id=producto.id,
                nombre=producto.nombre,
                descripcion=producto.descripcion,
                precio_regular=producto.precio_regular,
                precio_descuento=producto.precio_descuento,
                categoria=producto.categoria.nombre if producto.categoria else None,
                imagen_principal=(
                    producto.imagenes[0].url_imagen if producto.imagenes else None
                ),
                razon=rec.razon_ia or "",
                palabras_clave=rec.palabras_clave or [],
                score=rec.score,
            )
        )

    return AnalisisCompletoResponse(
        analisis_id=analisis.id,
        tipo_cuerpo=analisis.tipo_cuerpo_detectado,
        confianza=analisis.confianza,
        fecha_analisis=analisis.fecha_analisis,
        recomendaciones=productos_response,
        total_recomendaciones=len(productos_response),
    )


@router.post("/regenerar/{analisis_id}", response_model=AnalisisCompletoResponse)
def regenerar_recomendaciones(
    analisis_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Regenera recomendaciones para un análisis existente
    Útil si el usuario quiere ver opciones diferentes
    """
    analisis = (
        db.query(AnalisisMorfologico)
        .filter(
            AnalisisMorfologico.id == analisis_id,
            AnalisisMorfologico.usuario_id == current_user.id,
        )
        .first()
    )

    if not analisis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Análisis no encontrado"
        )

    # Eliminar recomendaciones anteriores
    db.query(RecomendacionGenerada).filter(
        RecomendacionGenerada.analisis_id == analisis_id
    ).delete()

    # Generar nuevas recomendaciones
    productos_recomendados = (
        recommendation_service.generar_recomendaciones_inteligentes(
            db=db,
            tipo_cuerpo=analisis.tipo_cuerpo_detectado,
            usuario_id=current_user.id,
            limite=10,
        )
    )

    # Generar explicaciones con IA
    productos_con_ia = ai_service.generar_explicaciones_batch(
        tipo_cuerpo=analisis.tipo_cuerpo_detectado,
        productos=productos_recomendados,
        usar_reasoning=True,
    )

    # Guardar nuevas recomendaciones
    for idx, prod in enumerate(productos_con_ia, start=1):
        recomendacion = RecomendacionGenerada(
            analisis_id=analisis.id,
            producto_id=UUID(prod["id"]),
            razon_ia=prod.get("razon"),
            palabras_clave=prod.get("palabras_clave", []),
            posicion=idx,
        )
        db.add(recomendacion)

    db.commit()

    # Retornar análisis completo
    return obtener_analisis_completo(analisis_id, db, current_user)


@router.post("/interaccion")
def registrar_interaccion(
    request: RegistrarInteraccionRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Registra cuando el usuario interactúa con una recomendación
    (click, agregar al carrito, compra)
    """
    recomendacion = (
        db.query(RecomendacionGenerada)
        .filter(RecomendacionGenerada.id == request.recomendacion_id)
        .first()
    )

    if not recomendacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recomendación no encontrada"
        )

    # Actualizar según tipo de interacción
    if request.tipo_interaccion == "click":
        recomendacion.fue_clickeado = True
    elif request.tipo_interaccion == "agregar_carrito":
        recomendacion.fue_agregado_carrito = True

    db.commit()

    return {"mensaje": "Interacción registrada correctamente"}


@router.get("/tipos-cuerpo")
def obtener_tipos_cuerpo():
    """
    Retorna los tipos de cuerpo disponibles
    """
    return {
        "tipos": [
            "Triangulo Invertido",
            "Reloj de Arena",
            "Rectangulo",
            "Triangulo",
            "Ovalo",
        ]
    }


@router.post("/test-clasificacion")
async def test_clasificacion(file: UploadFile = File(...)):
    """
    Endpoint de PRUEBA para clasificación
    No requiere autenticación ni guarda nada en BD
    Solo procesa la imagen y retorna el resultado
    """
    import tempfile

    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen (JPG, PNG, etc.)",
        )

    # Guardar temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        contents = await file.read()
        temp_file.write(contents)
        temp_path = temp_file.name

    try:
        from app.services import clasification_service

        print(f"\n{'='*50}")
        print(f" TEST DE CLASIFICACIÓN")
        print(f"{'='*50}")

        # Clasificar
        resultado = clasification_service.clasificar_tipo_cuerpo(temp_path)

        print(f"\n Resultado del test:")
        print(f"   Tipo: {resultado['tipo_cuerpo']}")
        print(f"   Confianza: {resultado['confianza']:.2%}")
        print(f"{'='*50}\n")

        # Eliminar imagen
        os.unlink(temp_path)

        return {
            "success": True,
            "tipo_cuerpo": resultado["tipo_cuerpo"],
            "confianza": resultado["confianza"],
            "tipo_cuerpo_original": resultado["tipo_cuerpo_original"],
            "probabilidades": resultado.get("probabilidades", {}),
            "mensaje": "Clasificación exitosa (modo prueba - no se guardó en BD)",
        }

    except Exception as e:
        # Asegurar eliminación de imagen
        if os.path.exists(temp_path):
            os.unlink(temp_path)

        print(f"❌ Error en test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en clasificación: {str(e)}",
        )


@router.get("/reglas/{tipo_cuerpo}")
def obtener_reglas(tipo_cuerpo: str, db: Session = Depends(get_db)):
    """
    Obtiene las reglas de recomendación para un tipo de cuerpo
    Útil para mostrar al usuario por qué se recomiendan ciertas categorías
    """
    reglas = recommendation_service.obtener_reglas_por_tipo(db, tipo_cuerpo)

    if not reglas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay reglas para el tipo de cuerpo: {tipo_cuerpo}",
        )

    return {"tipo_cuerpo": tipo_cuerpo, "reglas": reglas}


@router.post("/test-segmentacion")
async def test_segmentacion(file: UploadFile = File(...)):
    """
    Endpoint para VER SOLO la segmentación
    Retorna la imagen segmentada (fondo transparente)
    Útil para debuggear problemas de cobertura
    """
    from fastapi.responses import Response
    import tempfile
    import io

    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen",
        )

    # Guardar temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        contents = await file.read()
        temp_file.write(contents)
        temp_path = temp_file.name

    try:
        from app.services import clasification_service

        print("\n TEST DE SEGMENTACIÓN")

        # Solo segmentar (sin clasificar)
        img_segmentada = clasification_service.segmentar_imagen(temp_path, debug=False)

        # Convertir a bytes para retornar
        buf = io.BytesIO()
        img_segmentada.save(buf, format="PNG")
        buf.seek(0)

        # Eliminar imagen temporal
        os.unlink(temp_path)

        # Retornar imagen segmentada
        return Response(
            content=buf.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=segmentada.png"},
        )

    except Exception as e:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

        print(f" Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en segmentación: {str(e)}",
        )
