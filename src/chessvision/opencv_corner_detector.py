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
    
    warped_images = list(RESULTS_DIR.glob("warped_*.jpg"))
    if not warped_images:
        print(f"No se encontraron imágenes rectificadas en {RESULTS_DIR}")
        return

    # Patrón de esquinas interiores para 5x5 casillas centrales es 4x4
    pattern_size = (4, 4)

    for img_path in warped_images:
        print(f"\n--- Probando Crop Central (5x5 casillas): {img_path.name} ---")
        img = cv2.imread(str(img_path))
        if img is None: continue
        
        # 1. CROP CENTRAL DEL TABLERO (800x800)
        # 5 casillas de 100px cada una = 500px de ancho y alto
        # Centro: de (400-250) a (400+250) = de 150 a 650
        crop_size = 500
        start = (800 - crop_size) // 2
        end = start + crop_size
        img_crop = img[start:end, start:end]
        
        # 2. AGREGAR BORDE BLANCO (PADDING)
        border_size = 100
        img_padded = cv2.copyMakeBorder(
            img_crop, 
            border_size, border_size, border_size, border_size, 
            cv2.BORDER_CONSTANT, 
            value=[255, 255, 255]
        )
        
        gray = cv2.cvtColor(img_padded, cv2.COLOR_BGR2GRAY)
        
        # 3. Intentar detección SB (Sector Based) sobre el CROP
        ret, corners = cv2.findChessboardCornersSB(gray, pattern_size, 
                                                   cv2.CALIB_CB_EXHAUSTIVE + 
                                                   cv2.CALIB_CB_ACCURACY)

        if not ret:
            print("FALLO con SB en el CROP. Intentando con CLAHE...")
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray_clahe = clahe.apply(gray)
            ret, corners = cv2.findChessboardCornersSB(gray_clahe, pattern_size, cv2.CALIB_CB_EXHAUSTIVE)

        if ret:
            print(f"¡ÉXITO! Se detectaron las {pattern_size[0]*pattern_size[1]} esquinas centrales.")
            
            # Dibujar y Guardar
            cv2.drawChessboardCorners(img_padded, pattern_size, corners, ret)
            
            output_path = OPENCV_RESULTS_DIR / f"corners_crop_{img_path.name}"
            cv2.imwrite(str(output_path), img_padded)
            print(f"Imagen guardada: {output_path.name}")
        else:
            print("FALLO FINAL: No se detecta el patrón central. Es probable que la madera tenga poco contraste.")
            # Guardamos el crop para ver qué está viendo OpenCV
            cv2.imwrite(str(OPENCV_RESULTS_DIR / f"debug_crop_{img_path.name}"), img_padded)

if __name__ == "__main__":
    main()
