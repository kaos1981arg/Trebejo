import cv2
import numpy as np
import os
from pathlib import Path
from scipy.signal import find_peaks

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

def get_best_linear_fit(peaks):
    """
    Encuentra el inicio y el paso (step) que mejor se ajusta a los picos detectados.
    Calcula: peak_i = start + i * step
    """
    if len(peaks) < 2: return None, None
    
    # Calculamos las diferencias entre picos adyacentes para obtener el step promedio
    steps = np.diff(peaks)
    avg_step = np.mean(steps)
    
    # El primer pico detectado debería ser la línea 1 (100px ideal)
    # pero vamos a calcular el 'start' (línea 0) basándonos en todos los picos
    # i es el índice de la línea (1, 2, ..., len(peaks))
    starts = [p - (i+1)*avg_step for i, p in enumerate(peaks)]
    avg_start = np.mean(starts)
    
    return avg_start, avg_step

def main():
    warped_images = list(RESULTS_DIR.glob("warped_*.jpg"))
    if not warped_images: return

    for img_path in warped_images:
        print(f"\n--- Calibración Lineal Robusta: {img_path.name} ---")
        img = cv2.imread(str(img_path))
        if img is None: continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        row_profile = np.mean(gray, axis=1)
        col_profile = np.mean(gray, axis=0)

        # Detectar picos (valles invertidos)
        peaks_h, _ = find_peaks(-col_profile, distance=80, prominence=4)
        peaks_v, _ = find_peaks(-row_profile, distance=80, prominence=4)

        # Si detectamos los bordes (0 u 800), los filtramos para quedarnos con las interiores
        peaks_h = [p for p in peaks_h if 40 < p < 760]
        peaks_v = [p for p in peaks_v if 40 < p < 760]

        print(f"DEBUG: Líneas Verticales: {len(peaks_h)}, Horizontales: {len(peaks_v)}")

        # Ajuste Lineal para X (columnas) y Y (filas)
        start_x, step_x = get_best_linear_fit(peaks_h)
        start_y, step_y = get_best_linear_fit(peaks_v)

        if start_x is not None and start_y is not None:
            # Calculamos las coordenadas de los 4 bordes reales del tablero en la imagen
            x0, x8 = start_x, start_x + 8 * step_x
            y0, y8 = start_y, start_y + 8 * step_y
            
            print(f"DEBUG: Grid detectada -> X:({x0:.1f} a {x8:.1f}), Step:{step_x:.2f}")
            print(f"DEBUG: Grid detectada -> Y:({y0:.1f} a {y8:.1f}), Step:{step_y:.2f}")

            # Definimos los puntos de origen (el cuadrilátero real del tablero)
            src_pts = np.array([[x0, y0], [x8, y0], [x8, y8], [x0, y8]], dtype=np.float32)
            # Definimos el destino ideal (800x800)
            dst_pts = np.array([[0, 0], [800, 0], [800, 800], [0, 800]], dtype=np.float32)

            # Usamos Homografía solo para este recorte final (es más estable que un resize)
            M = cv2.getPerspectiveTransform(src_pts, dst_pts)
            final_img = cv2.warpPerspective(img, M, (800, 800))

            # Dibujar grilla de verificación
            for i in range(0, 801, 100):
                cv2.line(final_img, (i, 0), (i, 800), (0, 0, 255), 2)
                cv2.line(final_img, (0, i), (800, i), (0, 0, 255), 2)

            output_path = RESULTS_DIR / f"linear_calibrated_{img_path.name}"
            cv2.imwrite(str(output_path), final_img)
            print(f"¡ÉXITO! Tablero calibrado linealmente: {output_path.name}")
        else:
            print("ERROR: No se pudieron calcular los parámetros de la rejilla.")

if __name__ == "__main__":
    main()
