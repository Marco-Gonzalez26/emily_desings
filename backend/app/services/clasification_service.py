from PIL import Image
import numpy as np
from fastapi import HTTPException, status
import io
from scipy import ndimage
from rembg import remove, new_session
from typing import Dict
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
import torchvision.models as models
from pathlib import Path
from ultralytics import YOLO

import cv2



# Clases del modelo
CLASES = ["Apple", "Hourglass", "InvertedTriangle", "Rectangle", "Triangle"]

# Mapeo de clases del modelo a nombres en español
MAPEO_CLASES = {
    "Apple": "Ovalo",
    "Hourglass": "Reloj de Arena",
    "InvertedTriangle": "Triangulo Invertido",
    "Rectangle": "Rectangulo",
    "Triangle": "Triangulo",
}


# Sesiones globales (se cargan una sola vez)
_session_rembg = None
_modelo_clasificacion = None
yolo_model = None


def inicializar_modelos():
    """
    Pre-carga los modelos de IA en memoria al iniciar el servidor.
    Esto hace que el primer análisis sea tan rápido como los siguientes.

    Llamar desde main.py en el evento startup

    """
    print(" Inicializando modelos de IA")
    print("Cargando U2Net para segmentación")
    get_rembg_session()
    print(" Cargando ResNet34 para clasificación")
    cargar_modelo_clasificacion()
    print("Cargando Modelo YOLO para detección de persona")
    get_yolo_model()
    print("Yolo cargado")
    print("Modelos cargados")


def get_rembg_session():
    """Obtiene o crea la sesión de rembg (U2Net)"""
    global _session_rembg
    if _session_rembg is None:
        print("Inicializando U2Net para segmentación...")
        _session_rembg = new_session("u2net_human_seg")
        print("U2Net cargado")
    return _session_rembg


def get_yolo_model():
    """Obtiene o crea la sesión de YOLO"""
    global yolo_model
    if yolo_model is None:
        print("Inicializando YOLO...")
        yolo_model = YOLO("yolov8n.pt")
        print("YOLO cargado")
    return yolo_model


def validar_imagen_para_analisis(image_path: str) -> tuple[bool, str]:
    """
    Validar que la imagen contenga una persona usando YOLO
    """
    # Validar proporciones básicas

       
    if yolo_model is None:
        # Si YOLO no está disponible, solo validar por proporciones
        print("⚠️ YOLO no disponible, validando solo por proporciones")
        return True, ""

    try:
        # Detectar objetos en la imagen
        results = yolo_model(image_path, verbose=False)

        persona_detectada = False
        confianza_maxima = 0.0

        # Clase 0 en COCO dataset = persona
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                if class_id == 0:  # Persona
                    persona_detectada = True
                    confianza_maxima = max(confianza_maxima, confidence)

        if not persona_detectada:
            return (
                False,
                "No se detectó ninguna persona en la imagen. Por favor, sube una foto de cuerpo completo",
            )

        if confianza_maxima < 0.5:
            return (
                False,
                "La persona en la imagen no se ve con claridad. Por favor, sube una foto más nítida",
            )

        print(f" Persona detectada con confianza: {confianza_maxima:.2f}")
        return True, ""

    except Exception as e:
        print(f" Error en YOLO: {e}")
        # Si falla YOLO, continuar con solo validación de proporciones
        return True, ""


def cargar_modelo_clasificacion():
    """
    Carga tu modelo PyTorch ResNet34
    Se ejecuta UNA VEZ al inicio de la app
    """
    global _modelo_clasificacion

    if _modelo_clasificacion is None:
        print("Cargando modelo ResNet34...")

        # Crear arquitectura base ResNet34
        _modelo_clasificacion = models.resnet34(
            weights=None
        )  # Sin pesos pre-entrenados

        # Modificar classifier IGUAL que en tu entrenamiento
        num_features = _modelo_clasificacion.fc.in_features  # 512 para ResNet34
        _modelo_clasificacion.fc = nn.Sequential(
            nn.Dropout(0.6),
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 5),  # 5 clases
        )

        # Cargar checkpoint
        modelo_path = Path(__file__).parent.parent / "ai_models" / "emily_desings_ai.pt"
        checkpoint = torch.load(str(modelo_path), map_location=torch.device("cpu"))

        # Cargar pesos del state_dict
        _modelo_clasificacion.load_state_dict(checkpoint["model_state_dict"])

        # Modo evaluación
        _modelo_clasificacion.eval()

        # Info del checkpoint (opcional)
        epoch = checkpoint.get("epoch", "N/A")
        val_acc = checkpoint.get("val_acc", 0)

        print(f" Modelo ResNet34 cargado correctamente")
        if isinstance(epoch, int):
            print(f"   Entrenado hasta epoch: {epoch}")
        if val_acc > 0:
            print(f"   Mejor val accuracy: {val_acc:.2%}")

    return _modelo_clasificacion


def limpiar_mascara(alpha_np: np.ndarray, min_ratio: float = 0.15) -> np.ndarray:
    """
    Limpia la máscara alpha eliminando componentes pequeñas

    Args:
        alpha_np: Canal alpha de la imagen (0-255)
        min_ratio: Ratio mínimo de tamaño respecto al componente principal

    Returns:
        Máscara limpia (0-255)
    """
    binaria = alpha_np > 128
    etiquetada, n_componentes = ndimage.label(binaria)

    if n_componentes <= 1:
        return alpha_np

    tamanos = ndimage.sum(binaria, etiquetada, range(1, n_componentes + 1))
    componente_principal = np.argmax(tamanos) + 1
    umbral = tamanos[componente_principal - 1] * min_ratio

    mascara_limpia = np.zeros_like(binaria)
    for i, tam in enumerate(tamanos, start=1):
        if tam >= umbral:
            mascara_limpia |= etiquetada == i

    return (mascara_limpia * 255).astype(np.uint8)


def segmentar_imagen(
    img_path: str, crop_ratio: float = 0.55, debug: bool = False
) -> Image.Image:
    """
    Segmenta la imagen usando U2Net (rembg)

    Args:
        img_path: Path de la imagen temporal
        crop_ratio: Ratio de crop central si es necesario
        debug: Si True, guarda imágenes intermedias para inspección

    Returns:
        Imagen RGBA segmentada (fondo transparente)
    """
    session = get_rembg_session()
    img_original = Image.open(img_path).convert("RGBA")
    W, H = img_original.size

    def _segmentar(img_pil: Image.Image) -> Image.Image:
        """Helper para segmentar una imagen PIL"""
        buf = io.BytesIO()
        img_pil.convert("RGB").save(buf, format="PNG")
        output_bytes = remove(buf.getvalue(), session=session)
        return Image.open(io.BytesIO(output_bytes)).convert("RGBA")

    def _cobertura(img_rgba: Image.Image) -> float:
        """Porcentaje de píxeles no transparentes"""
        alpha = np.array(img_rgba.split()[3])
        return (alpha > 128).sum() / alpha.size

    # Segmentar imagen completa
    print(" Segmentando imagen completa...")
    seg_full = _segmentar(img_original)
    cobertura = _cobertura(seg_full)
    print(f"   Cobertura: {cobertura:.2%}")
    if debug:
        debug_path = img_path.replace(".jpg", "_segmentada.png").replace(
            ".jpeg", "_segmentada.png"
        )
        seg_full.save(debug_path)
        print(f"🔍 DEBUG: Imagen segmentada guardada en: {debug_path}")
    if cobertura >= 0.05:
        print("Segmentación completada")
        return seg_full
    # Segmentar con crop central si es necesario
    print("Intentando con crop central...")
    margen = int(W * (1 - crop_ratio) / 2)
    img_crop = img_original.crop((margen, 0, W - margen, H))
    seg_crop = _segmentar(img_crop)
    canvas = Image.new("RGBA", img_original.size, (0, 0, 0, 0))
    canvas.paste(seg_crop, (margen, 0))
    if debug:
        debug_path_crop = img_path.replace(".jpg", "_segmentada_crop.png").replace(
            ".jpeg", "_segmentada_crop.png"
        )
        canvas.save(debug_path_crop)
        print(f"🔍 DEBUG: Imagen con crop guardada en: {debug_path_crop}")
    print(" Segmentación con crop exitosa")
    return canvas


def preprocesar_imagen_para_modelo(img_pil: Image.Image) -> torch.Tensor:
    """
    Preprocesa la imagen segmentada para el modelo PyTorch

    Args:
        img_pil: Imagen PIL RGBA segmentada

    Returns:
        Tensor de PyTorch listo para el modelo
    """

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    # Convertir RGBA → RGB (eliminar canal alpha)
    img_rgb = img_pil.convert("RGB")

    # Aplicar transformaciones
    img_tensor = transform(img_rgb)

    # Agregar dimensión de batch [1, 3, 224, 224]
    img_batch = img_tensor.unsqueeze(0)

    return img_batch


def predecir_con_modelo(modelo, img_tensor: torch.Tensor) -> Dict:
    """
    Ejecuta predicción con el modelo PyTorch

    Args:
        modelo: Modelo PyTorch cargado
        img_tensor: Tensor preprocesado

    Returns:
        {
            "clase": str,
            "confianza": float,
            "probabilidades": dict
        }
    """
    # Asegurar que el modelo está en modo evaluación
    modelo.eval()

    # Predicción sin calcular gradientes
    with torch.no_grad():
        outputs = modelo(img_tensor)

        # Aplicar softmax para obtener probabilidades
        probabilities = F.softmax(outputs, dim=1)[0]

    # Obtener clase con mayor probabilidad
    confianza, idx = torch.max(probabilities, dim=0)
    clase_predicha = CLASES[idx.item()]

    # Crear diccionario de probabilidades
    probabilidades = {
        CLASES[i]: float(probabilities[i].item()) for i in range(len(CLASES))
    }

    return {
        "clase": clase_predicha,
        "confianza": float(confianza.item()),
        "probabilidades": probabilidades,
    }


def clasificar_tipo_cuerpo(img_path: str, debug: bool = False) -> Dict[str, any]:
    """
    Pipeline completo: Segmentación + Clasificación

    Args:
        img_path: Path de la imagen temporal
        debug: Si True, guarda imágenes intermedias para inspección

    Returns:
        {
            "tipo_cuerpo": str (en español, ej: "Triangulo Invertido"),
            "confianza": float (0.0 - 1.0),
            "tipo_cuerpo_original": str (en inglés, ej: "InvertedTriangle"),
            "probabilidades": dict (todas las clases con sus scores)
        }
    """

    # Detectar persona con MediaPipe
    es_valido, mensaje_error = validar_imagen_para_analisis(img_path)
    if not es_valido:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=mensaje_error)
        return

    print("\n Segmentación")
    img_segmentada = segmentar_imagen(img_path, debug=debug)

    # Aplicar limpieza de máscara
    alpha_np = np.array(img_segmentada.split()[3])
    alpha_limpia = limpiar_mascara(alpha_np)
    img_limpia = img_segmentada.copy()
    img_limpia.putalpha(Image.fromarray(alpha_limpia))

    #  Clasificación con modelo PyTorch
    print("\n Clasificación")

    # Cargar modelo (se carga una sola vez)
    modelo = cargar_modelo_clasificacion()

    # Preprocesar imagen
    img_tensor = preprocesar_imagen_para_modelo(img_limpia)

    # Predecir
    resultado_modelo = predecir_con_modelo(modelo, img_tensor)

    # Mapear clase en inglés a español
    tipo_cuerpo_ingles = resultado_modelo["clase"]
    tipo_cuerpo_espanol = MAPEO_CLASES.get(tipo_cuerpo_ingles, tipo_cuerpo_ingles)

    print(f" Clasificación: {tipo_cuerpo_ingles} → {tipo_cuerpo_espanol}")
    print(f"   Confianza: {resultado_modelo['confianza']:.2%}")

    return {
        "tipo_cuerpo": tipo_cuerpo_espanol,
        "confianza": resultado_modelo["confianza"],
        "tipo_cuerpo_original": tipo_cuerpo_ingles,
        "probabilidades": resultado_modelo.get("probabilidades", {}),
    }
