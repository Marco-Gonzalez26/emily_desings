import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from PIL import Image
import torch

from app.services.clasification_service import (
    limpiar_mascara,
    preprocesar_imagen_para_modelo,
    predecir_con_modelo,
    CLASES,
    MAPEO_CLASES,
)



class TestLimpiarMascara:
    def test_retorna_misma_mascara_si_un_componente(self):
        alpha = np.zeros((100, 100), dtype=np.uint8)
        alpha[10:90, 10:90] = 255
        result = limpiar_mascara(alpha)
        assert result.shape == alpha.shape

    def test_elimina_componentes_pequeños(self):
        alpha = np.zeros((100, 100), dtype=np.uint8)
        # Componente principal grande
        alpha[10:80, 10:80] = 255
        # Componente pequeño (ruido)
        alpha[95:99, 95:99] = 255

        result = limpiar_mascara(alpha)

        # El componente pequeño debe eliminarse
        assert result[97, 97] == 0
        # El componente principal debe conservarse
        assert result[40, 40] == 255

    def test_retorna_mascara_cuando_todo_es_cero(self):
        alpha = np.zeros((50, 50), dtype=np.uint8)
        result = limpiar_mascara(alpha)
        assert result.shape == alpha.shape



class TestPreprocesarImagenParaModelo:
    def test_retorna_tensor_con_forma_correcta(self):
        img = Image.new("RGBA", (300, 400), (128, 64, 32, 255))
        tensor = preprocesar_imagen_para_modelo(img)

        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape == (1, 3, 224, 224)

    def test_tensor_tiene_valores_normalizados(self):
        img = Image.new("RGBA", (224, 224), (255, 255, 255, 255))
        tensor = preprocesar_imagen_para_modelo(img)

        # Con normalización ImageNet los valores no deben estar en [0,1]
        assert tensor.min().item() < 0 or tensor.max().item() > 1

    def test_acepta_imagen_rgba(self):
        img = Image.new("RGBA", (100, 100), (200, 100, 50, 200))
        tensor = preprocesar_imagen_para_modelo(img)
        assert tensor.shape == (1, 3, 224, 224)



class TestPredecirConModelo:
    def _crear_modelo_mock(self, clase_idx: int = 0):
        modelo = MagicMock()
        logits = torch.zeros(1, 5)
        logits[0, clase_idx] = 10.0  # Alta confianza en la clase
        modelo.return_value = logits
        modelo.eval = MagicMock()
        return modelo

    def test_retorna_estructura_correcta(self):
        modelo = self._crear_modelo_mock(clase_idx=2)
        tensor = torch.zeros(1, 3, 224, 224)

        result = predecir_con_modelo(modelo, tensor)

        assert "clase" in result
        assert "confianza" in result
        assert "probabilidades" in result

    def test_clase_predicha_es_valida(self):
        modelo = self._crear_modelo_mock(clase_idx=1)
        tensor = torch.zeros(1, 3, 224, 224)

        result = predecir_con_modelo(modelo, tensor)

        assert result["clase"] in CLASES

    def test_confianza_esta_entre_0_y_1(self):
        modelo = self._crear_modelo_mock(clase_idx=0)
        tensor = torch.zeros(1, 3, 224, 224)

        result = predecir_con_modelo(modelo, tensor)

        assert 0.0 <= result["confianza"] <= 1.0

    def test_probabilidades_suman_1(self):
        modelo = self._crear_modelo_mock(clase_idx=3)
        tensor = torch.zeros(1, 3, 224, 224)

        result = predecir_con_modelo(modelo, tensor)
        total = sum(result["probabilidades"].values())

        assert abs(total - 1.0) < 1e-5

    def test_probabilidades_contienen_todas_las_clases(self):
        modelo = self._crear_modelo_mock(clase_idx=0)
        tensor = torch.zeros(1, 3, 224, 224)

        result = predecir_con_modelo(modelo, tensor)

        for clase in CLASES:
            assert clase in result["probabilidades"]

    def test_predice_clase_con_mayor_logit(self):
        modelo = self._crear_modelo_mock(clase_idx=4)
        tensor = torch.zeros(1, 3, 224, 224)

        result = predecir_con_modelo(modelo, tensor)

        assert result["clase"] == CLASES[4]



class TestMapeoClases:
    def test_todas_las_clases_tienen_mapeo(self):
        for clase in CLASES:
            assert clase in MAPEO_CLASES

    def test_mapeo_retorna_nombres_en_espanol(self):
        assert MAPEO_CLASES["Apple"] == "Ovalo"
        assert MAPEO_CLASES["Hourglass"] == "Reloj de Arena"
        assert MAPEO_CLASES["InvertedTriangle"] == "Triangulo Invertido"
        assert MAPEO_CLASES["Rectangle"] == "Rectangulo"
        assert MAPEO_CLASES["Triangle"] == "Triangulo"