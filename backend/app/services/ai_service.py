import os
from openai import OpenAI
from typing import List, Dict, Optional
import json


_client = None


def get_openrouter_client() -> OpenAI:
    """Obtiene o crea el cliente de OpenRouter"""
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPEN_ROUTER_API_KEY"),
        )
    return _client



MODELO_IA = "openai/gpt-oss-120b:free"


def generar_explicacion_producto(
    tipo_cuerpo: str, producto_nombre: str, categoria: str, max_tokens: int = 150
) -> str:
    """
    Genera una explicación personalizada de por qué un producto es recomendado
    """
    client = get_openrouter_client()

    prompt = f"""
Tipo de cuerpo: {_formatear_tipo_cuerpo(tipo_cuerpo)}
Prenda: {producto_nombre}
Categoría: {categoria}

Explica en 2-3 oraciones por qué esta prenda favorece este tipo de cuerpo.
Menciona principios de diseño: equilibrio visual, proporciones, líneas.
Sé específica y entusiasta.
"""

    try:
        response = client.chat.completions.create(
            model=MODELO_IA,
            messages=[
                {
                    "role": "system",
                    "content": "Eres una asesora de moda experta en morfología corporal. "
                    "Explicas en español por qué cada prenda favorece el tipo de cuerpo. "
                    "Usas lenguaje profesional pero accesible. 2-3 oraciones máximo. "
                    "Varía tus explicaciones para mantener interés.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )

        explicacion = response.choices[0].message.content.strip()
        
        # Validación básica
        if len(explicacion) < 10:
            return _explicacion_fallback(tipo_cuerpo, categoria)
            
        return explicacion

    except Exception as e:
        print(f"Error con OpenRouter: {e}")
        return _explicacion_fallback(tipo_cuerpo, categoria)


def generar_explicaciones_batch(
    tipo_cuerpo: str, productos: List[Dict], usar_reasoning: bool = True
) -> List[Dict]:
    """
    Genera explicaciones para múltiples productos usando structured output
    y reasoning enabled para análisis más profundo

    Args:
        tipo_cuerpo: Tipo de cuerpo
        productos: Lista de productos con {id, nombre, categoria, precio}
        usar_reasoning: Si True, usa chain-of-thought para mejores explicaciones

    Returns:
        Lista de productos con explicaciones agregadas
    """
    client = get_openrouter_client()


    productos_info = []
    for p in productos:
        productos_info.append(
            {
                "id": str(p.get("id")),
                "nombre": p.get("nombre"),
                "categoria": p.get("categoria"),
                "precio": str(p.get("precio", "N/A")),
            }
        )

    prompt = f"""
Tipo de cuerpo: {_formatear_tipo_cuerpo(tipo_cuerpo)}

Productos a analizar:
{json.dumps(productos_info, indent=2, ensure_ascii=False)}

Para cada producto, genera:
1. Una explicación de 2-3 oraciones sobre por qué favorece este tipo de cuerpo
2. 2-3 palabras clave (ej: "equilibrio visual", "cintura definida", "volumen inferior")

Responde SOLO con JSON siguiendo este formato:
{{
  "explicaciones": [
    {{
      "producto_id": "id_del_producto",
      "razon": "Explicación detallada basada en principios de diseño...",
      "palabras_clave": ["palabra1", "palabra2"]
    }}
  ]
}}
"""

    try:
        request_params = {
            "model": MODELO_IA,
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un experto en moda y análisis morfológico corporal. "
                    "Aplicas principios de diseño, teoría del color, y proporciones "
                    "para explicar por qué ciertas prendas favorecen tipos de cuerpo específicos. "
                    "Respondes SOLO con JSON válido, sin texto adicional.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 2000,
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
        }


        if usar_reasoning:
            request_params["extra_body"] = {"reasoning": {"enabled": True}}

        response = client.chat.completions.create(**request_params)

        contenido = response.choices[0].message.content.strip()

 
        if contenido.startswith("```json"):
            contenido = contenido.replace("```json", "").replace("```", "").strip()

        resultado = json.loads(contenido)
        explicaciones_dict = {
            exp["producto_id"]: exp for exp in resultado.get("explicaciones", [])
        }


        for prod in productos:
            prod_id = str(prod.get("id"))
            if prod_id in explicaciones_dict:
                exp = explicaciones_dict[prod_id]
                prod["razon"] = exp["razon"]
                prod["palabras_clave"] = exp.get("palabras_clave", [])
            else:
                prod["razon"] = _explicacion_fallback(
                    tipo_cuerpo, prod.get("categoria")
                )
                prod["palabras_clave"] = []

        return productos

    except Exception as e:
        print(f"Error en batch con structured output: {e}")

        for prod in productos:
            prod["razon"] = _explicacion_fallback(tipo_cuerpo, prod.get("categoria"))
            prod["palabras_clave"] = []
        return productos


def _formatear_tipo_cuerpo(tipo: str) -> str:
    """Convierte el tipo de cuerpo a formato legible con características"""
    tipos = {
        "Triangulo Invertido": "Triángulo Invertido - Hombros anchos, cintura definida, caderas estrechas",
        "Reloj de Arena": "Reloj de Arena - Hombros y caderas equilibrados, cintura marcada y definida",
        "Rectangulo": "Rectángulo - Hombros, cintura y caderas alineados, silueta recta",
        "Triangulo": "Triángulo o Pera - Caderas más anchas que hombros, cintura definida",
        "Ovalo": "Óvalo o Manzana - Volumen concentrado en la parte central del cuerpo",
    }
    return tipos.get(tipo, tipo)


def _explicacion_fallback(tipo_cuerpo: str, categoria: str) -> str:
    """Explicación genérica de alta calidad si falla la IA"""
    explicaciones = {
        "Triangulo Invertido": {
            "Pantalones": "Añade volumen visual en la parte inferior para balancear hombros anchos y crear proporciones armoniosas.",
            "Faldas": "Crea equilibrio visual ampliando la silueta en la zona de caderas, compensando hombros prominentes.",
            "Vestidos": "El corte en línea A favorece tu figura al equilibrar las proporciones entre la parte superior e inferior.",
            "Tops": "Los escotes en V alargan el torso y crean líneas verticales que estilizan la figura.",
            "Camisetas": "Los escotes en V alargan el torso y crean líneas verticales que estilizan la figura.",
        },
        "Reloj de Arena": {
            "Vestidos": "Resalta tu cintura naturalmente definida y celebra tus curvas balanceadas.",
            "Tops": "Los cortes ajustados en cintura destacan tus proporciones equilibradas perfectamente.",
            "Camisetas": "Los cortes ajustados en cintura destacan tus proporciones equilibradas perfectamente.",
            "Pantalones": "Los cortes que marcan cintura realzan tu silueta naturalmente curvilínea.",
            "Faldas": "Enfatiza tu cintura definida y balancea tus proporciones ya equilibradas.",
        },
        "Rectangulo": {
            "Vestidos": "Crea la ilusión de curvas y define la zona de cintura con cortes estratégicos.",
            "Tops": "Los detalles en cintura añaden dimensión y crean puntos de interés visual.",
            "Camisetas": "Los detalles en cintura añaden dimensión y crean puntos de interés visual.",
            "Pantalones": "Los tiros altos definen visualmente tu cintura y crean proporciones femeninas.",
            "Faldas": "Añade volumen y movimiento para crear curvas y definir la silueta.",
        },
        "Triangulo": {
            "Tops": "Añade volumen visual en hombros para balancear caderas más anchas.",
            "Camisetas": "Añade volumen visual en hombros para balancear caderas más anchas.",
            "Vestidos": "El corte imperio o línea A equilibra proporciones entre parte superior e inferior.",
            "Pantalones": "Los cortes rectos o ligeramente acampanados armonizan la silueta completa.",
            "Chaquetas": "Estructuradas en hombros crean balance con la zona de caderas.",
        },
        "Ovalo": {
            "Vestidos": "Los cortes imperio desvían atención de la zona central hacia piernas y escote.",
            "Tops": "Los escotes en V crean líneas verticales que alargan y estilizan el torso.",
            "Camisetas": "Los escotes en V crean líneas verticales que alargan y estilizan el torso.",
            "Pantalones": "Los cortes rectos balancean proporciones y alargan la silueta visualmente.",
            "Chaquetas": "Las líneas verticales crean un efecto alargador que favorece tu figura.",
        },
    }

    tipo_explicaciones = explicaciones.get(tipo_cuerpo, {})
    return tipo_explicaciones.get(
        categoria,
        "Esta prenda está diseñada para complementar y realzar tu tipo de figura específico.",
    )
