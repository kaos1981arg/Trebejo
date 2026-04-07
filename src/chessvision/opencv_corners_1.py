import cv2
import numpy as np
import os
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
OPENCV_RESULTS_DIR = BASE_DIR / "opencv_tests"


def main():
    if not os.path.exists(OPENCV_RESULTS_DIR):
        os.makedirs(OPENCV_RESULTS_DIR)

    warped_images = list(RESULTS_DIR.glob("warped_*.jpg"))
    if not warped_images:
        print(f"No se encontraron imágenes rectificadas en {RESULTS_DIR}")
        return

    pattern_size = (5, 5)

    for img_path in warped_images:
        print(f"\n--- Probando OpenCV Robusto (SB) en: {img_path.name} ---")
        img = cv2.imread(str(img_path))
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # --- MÉTODO 1: findChessboardCornersSB (Sector Based) ---
        # Este método es ideal para tableros de madera y con perspectiva corregida
        ret, corners = cv2.findChessboardCornersSB(
            gray, pattern_size, cv2.CALIB_CB_EXHAUSTIVE + cv2.CALIB_CB_ACCURACY
        )

        if not ret:
            print(
                "FALLO con SB inicial. Intentando Umbralización de Otsu (Blanco y Negro puro)..."
            )
            # --- MÉTODO 2: Umbralización de Otsu ---
            # Esto separa el marrón del blanco forzando a BN puro
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Guardamos el thresh para depuración
            cv2.imwrite(
                str(OPENCV_RESULTS_DIR / f"debug_thresh_{img_path.name}"), thresh
            )
            ret, corners = cv2.findChessboardCornersSB(
                thresh, pattern_size, cv2.CALIB_CB_EXHAUSTIVE
            )

        if ret:
            print(
                f"¡ÉXITO! Se detectaron las {pattern_size[0]*pattern_size[1]} esquinas."
            )
            cv2.drawChessboardCorners(img, pattern_size, corners, ret)
            output_path = OPENCV_RESULTS_DIR / f"corners_sb_{img_path.name}"
            cv2.imwrite(str(output_path), img)
            print(f"Imagen guardada: {output_path.name}")
        else:
            print("FALLO TOTAL. OpenCV no ve el patrón 7x7.")


if __name__ == "__main__":
    main()
