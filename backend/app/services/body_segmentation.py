import os
import cv2
import torch
import numpy as np
from torchvision import transforms
from torchvision.models.segmentation import deeplabv3_resnet50
from PIL import Image
import time
from pathlib import Path
from tqdm import tqdm
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class BodySegmentation:

    def __init__(self, device="cpu"):
        self.device = device
        self.model = self._load_deeplab()
        self.model_path = self._download_medidapipe_model()

        base_options = python.BaseOptions(model_asset_path=str(self.model_path))
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=False,
            running_mode=vision.RunningMode.IMAGE,
            min_pose_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.pose_detector = vision.PoseLandmarker.create_from_options(options)

        self.preprocess = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    def _download_medidapipe_model(self):
        """
        Descarga el modelo MediaPipe de PoseLandmarker.
        """
        model_dir = Path("app/ai_models")
        model_dir.mkdir(exist_ok=True, parents=True)
        model_path = model_dir / "pose_landmarker_heavy.task"

        if not model_path.exists():
            import urllib.request

            print("Descargando modelo MediaPipe…")
            url = "https://storage.googleapis.com/mediapipe-assets/pose_landmarker/pose_landmarker_heavy.task"
            urllib.request.urlretrieve(url, str(model_path))
            print("Modelo descargado.")

        return model_path

    def _load_deeplab(self):
        """
        Carga el modelo DeepLabV3 ResNet50 pre-entrenado.
        """
        print(f"Cargando modelo DeepLabV3 ResNet50 en {self.device}")
        model = deeplabv3_resnet50(weights="DEFAULT")
        model.eval()
        model.to(self.device)
        print("Modelo cargado.")
        return model

    def segment_person(self, bgr_img):
        """
        Segmenta una imagen en máscara binaria.
        Returns: mascara binaria (array numpy)
        """
        rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)

        inp = self.preprocess(pil_img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            out = self.model(inp)["out"][0]
            mask = out.argmax(0).cpu().numpy()

        # Limpieza de mascara
        kernel = np.ones((5, 5), np.uint8)
        person = cv2.morphologyEx(person, cv2.MORPH_OPEN, kernel)
        person = cv2.morphologyEx(person, cv2.MORPH_CLOSE, kernel)
        return person

    def extract_keypoints(self, bgr_img):
        """
        Extrae los puntos de la imagen.
        Returns: diccionario con coornedadas de las landmarks
        """
        rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)

        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.pose_detector.detect(mp_img)

        if not result.pose_landmarks:
            return None

        h, w = bgr_img.shape[:2]
        person_landmarks = result.pose_landmarks[0]
        keypoints = {}

        KEY_INDICES = {
            "left_shoulder": 11,
            "right_shoulder": 12,
            "left_elbow": 13,
            "right_elbow": 14,
            "left_hip": 23,
            "right_hip": 24,
        }

        for name, index in KEY_INDICES.items():
            landmark = person_landmarks[index]
            keypoints[name] = {
                "x": landmark.x * w,
                "y": landmark.y * h,
                "visibility": landmark.visibility,
            }

        return keypoints

    def calculate_body_ratios(self, keypoints):
        """
        Calcula proporciones corporales.
        Returns: diccionario con proporciones corporales
        """
        if not keypoints:
            return None

        # Ancho de los hombros
        shoulder_width = abs(
            keypoints["left_shoulder"]["x"] - keypoints["right_shoulder"]["x"]
        )

        # Ancho de caderas
        hip_width = abs(keypoints["left_hip"]["x"] - keypoints["right_hip"]["x"])

        if hip_width == 0:
            return None

        ratios = {
            "shoulder_width": shoulder_width,
            "hip_width": hip_width,
            "shoulder_hip_ratio": shoulder_width / hip_width,
            "hip_shoulder_ratio": hip_width / shoulder_width,
        }

        return ratios

    def crop_img_to_body(self, img, mask, padding=20):
        """
        Recortar la imagen enfocandose solo en el cuerpo segmentado
        """

        ys, xs = np.where(mask > 0)

        if len(xs) == 0:
            return None

        x1, x2 = xs.min(), xs.max()
        y1, y2 = ys.min(), ys.max()

        h, w = img.shape[:2]

        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(w, x2 + padding)
        y2 = min(h, y2 + padding)

        return img[y1:y2, x1:x2]

    def process_single_image(
        self,
        input_path,
        output_dir,
        save_mask=True,
        save_crop=True,
        save_keypoints=True,
    ):
        """
        Procesa una imagen completa: segmentación + keypoints + features
        """
        # Leer imagen
        img = cv2.imread(str(input_path))
        if img is None:
            print(f"❌ Error leyendo: {input_path}")
            return None

        results = {}
        img_name = Path(input_path).stem

        # 1. Segmentación
        mask = self.segment_person(img)
        results["mask"] = mask

        if save_mask:
            mask_path = Path(output_dir) / "masks" / f"{img_name}_mask.png"
            mask_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(mask_path), mask)
            results["mask_path"] = str(mask_path)

        # 2. Recorte
        if save_crop:
            cropped = self.crop_img_to_body(img, mask)
            if cropped is not None:
                crop_path = Path(output_dir) / "cropped" / f"{img_name}.jpg"
                crop_path.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(crop_path), cropped)
                results["crop_path"] = str(crop_path)

        # 3. Keypoints
        keypoints = self.extract_keypoints(img)
        results["keypoints"] = keypoints

        if save_keypoints and keypoints:
            # Dibujar keypoints en imagen
            img_with_kp = img.copy()
            for name, kp in keypoints.items():
                cv2.circle(
                    img_with_kp, (int(kp["x"]), int(kp["y"])), 5, (0, 255, 0), -1
                )

            kp_path = Path(output_dir) / "keypoints" / f"{img_name}_kp.jpg"
            kp_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(kp_path), img_with_kp)
            results["keypoints_path"] = str(kp_path)

        # 4. Calcular ratios
        ratios = self.calculate_body_ratios(keypoints)
        results["ratios"] = ratios

        return results

    def process_dataset(
        self, input_folder="app/dataset_raw", output_folder="app/dataset_processed"
    ):
        """
        Procesa todo el dataset organizado por categorías
        """
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        output_path.mkdir(exist_ok=True)

        # Buscar todas las categorías
        categories = [d for d in input_path.iterdir() if d.is_dir()]

        if not categories:
            print("⚠️ No se encontraron carpetas de categorías")
            print("Procesando imágenes directamente...")
            categories = [input_path]

        total_processed = 0
        total_failed = 0

        for category_dir in categories:
            category_name = category_dir.name
            print(f"\n📁 Procesando categoría: {category_name}")

            # Buscar imágenes
            image_files = (
                list(category_dir.glob("*.jpg"))
                + list(category_dir.glob("*.jpeg"))
                + list(category_dir.glob("*.png"))
            )

            if not image_files:
                print(f"  ⚠️ No se encontraron imágenes en {category_name}")
                continue
            print(f"  Encontradas {len(image_files)} imágenes")
            output_path / category_name.mkdir(exist_ok=True)
            for img_file in tqdm(image_files, desc=f"  {category_name}"):
                try:
                    results = self.process_single_image(
                        img_file,
                        category_output,
                        save_mask=True,
                        save_crop=True,
                        save_keypoints=True,
                    )

                    if results:
                        total_processed += 1
                    else:
                        total_failed += 1

                except Exception as e:
                    print(f"\n  ❌ Error procesando {img_file.name}: {e}")
                    total_failed += 1

        print(f"\n{'='*60}")
        print(f"✅ Procesamiento completado:")
        print(f"   Total procesadas: {total_processed}")
        print(f"   Total fallidas: {total_failed}")
        print(f"   Carpeta de salida: {output_path}")
        print(f"{'='*60}")


# -----------------------------------------------------------
# MAIN
# -----------------------------------------------------------
if __name__ == "__main__":
    # Detectar si hay GPU disponible
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🖥️  Usando: {device.upper()}")

    # Crear pipeline
    pipeline = BodySegmentation(device=device)

    # Procesar dataset completo
    pipeline.process_dataset(
        input_folder="app/dataset_raw", output_folder="app/dataset_processed"
    )
