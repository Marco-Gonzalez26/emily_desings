import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.services.ai_service import (
    generar_explicacion_producto,
    generar_explicaciones_batch,
    _formatear_tipo_cuerpo,
    _explicacion_fallback,
)



class TestFormatearTipoCuerpo:
    def test_formatea_triangulo_invertido(self):
        result = _formatear_tipo_cuerpo("Triangulo Invertido")
        assert "Triángulo Invertido" in result
        assert "Hombros anchos" in result

    def test_formatea_reloj_de_arena(self):
        result = _formatear_tipo_cuerpo("Reloj de Arena")
        assert "Reloj de Arena" in result

    def test_retorna_tipo_original_si_no_existe(self):
        result = _formatear_tipo_cuerpo("TipoDesconocido")
        assert result == "TipoDesconocido"

    @pytest.mark.parametrize("tipo", [
        "Triangulo Invertido",
        "Reloj de Arena",
        "Rectangulo",
        "Triangulo",
        "Ovalo",
    ])
    def test_todos_los_tipos_tienen_descripcion(self, tipo):
        result = _formatear_tipo_cuerpo(tipo)
        assert len(result) > len(tipo)



class TestExplicacionFallback:
    def test_retorna_explicacion_para_tipo_y_categoria_conocidos(self):
        result = _explicacion_fallback("Triangulo Invertido", "Pantalones")
        assert isinstance(result, str)
        assert len(result) > 10

    def test_retorna_explicacion_generica_si_categoria_no_existe(self):
        result = _explicacion_fallback("Triangulo Invertido", "CategoriaRara")
        assert "tipo de figura" in result.lower() or len(result) > 10

    def test_retorna_explicacion_generica_si_tipo_no_existe(self):
        result = _explicacion_fallback("TipoRaro", "Vestidos")
        assert isinstance(result, str)
        assert len(result) > 0



class TestGenerarExplicacionProducto:
    @patch("app.services.ai_service.get_openrouter_client")
    def test_retorna_explicacion_del_modelo(self, mock_client):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Esta prenda favorece tu tipo de cuerpo por sus líneas verticales."
        mock_client().chat.completions.create.return_value = mock_response

        result = generar_explicacion_producto("Triangulo", "Camiseta Rayas", "Tops")

        assert isinstance(result, str)
        assert len(result) > 10

    @patch("app.services.ai_service.get_openrouter_client")
    def test_usa_fallback_si_respuesta_muy_corta(self, mock_client):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Ok"
        mock_client().chat.completions.create.return_value = mock_response

        result = generar_explicacion_producto("Ovalo", "Vestido Largo", "Vestidos")

        assert isinstance(result, str)
        assert len(result) > 10

    @patch("app.services.ai_service.get_openrouter_client")
    def test_usa_fallback_si_falla_la_api(self, mock_client):
        mock_client().chat.completions.create.side_effect = Exception("API Error")

        result = generar_explicacion_producto("Rectangulo", "Jean Recto", "Pantalones")

        assert isinstance(result, str)
        assert len(result) > 10



class TestGenerarExplicacionesBatch:
    @patch("app.services.ai_service.get_openrouter_client")
    def test_agrega_razon_a_cada_producto(self, mock_client):
        prod_id = str(uuid4())
        productos = [
            {"id": prod_id, "nombre": "Vestido Floral", "categoria": "Vestidos", "precio": "45.00"}
        ]

        mock_response = MagicMock()
        mock_response.choices[0].message.content = f"""{{
            "explicaciones": [
                {{
                    "producto_id": "{prod_id}",
                    "razon": "Esta prenda realza tu figura con su corte en A.",
                    "palabras_clave": ["equilibrio visual", "cintura definida"]
                }}
            ]
        }}"""
        mock_client().chat.completions.create.return_value = mock_response

        result = generar_explicaciones_batch("Triangulo", productos)

        assert "razon" in result[0]
        assert "palabras_clave" in result[0]
        assert len(result[0]["razon"]) > 10

    @patch("app.services.ai_service.get_openrouter_client")
    def test_usa_fallback_si_falla_la_api(self, mock_client):
        mock_client().chat.completions.create.side_effect = Exception("API Error")
        productos = [
            {"id": str(uuid4()), "nombre": "Top Floral", "categoria": "Tops", "precio": "25.00"}
        ]

        result = generar_explicaciones_batch("Reloj de Arena", productos)

        assert "razon" in result[0]
        assert result[0]["palabras_clave"] == []

    @patch("app.services.ai_service.get_openrouter_client")
    def test_producto_sin_match_usa_fallback(self, mock_client):
        productos = [
            {"id": str(uuid4()), "nombre": "Blusa", "categoria": "Tops", "precio": "30.00"}
        ]

        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"explicaciones": []}'
        mock_client().chat.completions.create.return_value = mock_response

        result = generar_explicaciones_batch("Triangulo Invertido", productos)

        assert "razon" in result[0]