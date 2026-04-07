import cv2
import numpy as np
import os
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
OPENCV_RESULTS_DIR = BASE_DIR / "opencv_tests"

def main():
    if not os.path.exists(OPENCV_RESULTS_DIR): os.makedirs(OPENCV_RESULTS_DIR)
    
    # Buscamos las imágenes rectificadas (warped)
    warped_images = list(RESULTS_DIR.glob("warped_*.jpg"))
    if not warped_images:
        print(f"No se encontraron imágenes rectificadas en {RESULTS_DIR}")
        return

    # Patrón de esquinas interiores para un tablero de 8x8 casillas es 7x7
    pattern_size = (7, 7)

    for img_path in warped_images:
        print(f"\n--- Probando OpenCV en: {img_path.name} ---")
        img = cv2.imread(str(img_path))
        if img is None: continue
        
        # 1. Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Intentar encontrar esquinas (con diferentes flags para mayor robustez)
        # CALIB_CB_ADAPTIVE_THRESH: Usa umbralización adaptativa (mejor para iluminación desigual)
        # CALIB_CB_NORMALIZE_IMAGE: Normaliza la imagen antes de buscar
        ret, corners = cv2.findChessboardCorners(gray, pattern_size, 
                                                cv2.CALIB_CB_ADAPTIVE_THRESH + 
                                                cv2.CALIB_CB_NORMALIZE_IMAGE + 
                                                cv2.CALIB_CB_FAST_CHECK)

        if ret:
            print(f"¡ÉXITO! Se detectaron las {pattern_size[0]*pattern_size[1]} esquinas interiores.")
            
            # Refinar la precisión (Sub-píxel)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            
            # Dibujar las esquinas detectadas
            cv2.drawChessboardCorners(img, pattern_size, corners2, ret)
            
            output_path = OPENCV_RESULTS_DIR / f"corners_{img_path.name}"
            cv2.imwrite(str(output_path), img)
            print(f"Imagen guardada en: {output_path.name}")
        else:
            print("FALLO: No se detectó el patrón de 7x7. Probando pre-procesamiento agresivo...")
            
            # Re-intento con Ecualización de Histograma (CLAHE)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray_clahe = clahe.apply(gray)
            ret, corners = cv2.findChessboardCorners(gray_clahe, pattern_size, cv2.CALIB_CB_ADAPTIVE_THRESH)
            
            if ret:
                print("¡ÉXITO (con CLAHE)! Esquinas detectadas.")
                cv2.drawChessboardCorners(img, pattern_size, corners, ret)
                cv2.imwrite(str(OPENCV_RESULTS_DIR / f"corners_clahe_{img_path.name}"), img)
            else:
                print("FALLO DEFINITIVO: El patrón no es visible o las piezas lo tapan demasiado.")

if __name__ == "__main__":
    main()
