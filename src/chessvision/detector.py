import os
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "best.pt"
SAMPLES_DIR = BASE_DIR / "samples"
RESULTS_DIR = BASE_DIR / "results"

# Coordenadas ideales del centro de cada pieza en un tablero de 800x800
IDEAL_CENTERS = {
    "a1": [50, 750],   "h1": [750, 750],
    "a8": [50, 50],    "h8": [750, 50],
    "b2": [150, 650],  "g2": [650, 650],
    "b7": [150, 150],  "g7": [650, 150]
}

def get_distance(p1, p2):
    if p1 is None or p2 is None: return float('inf')
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def main():
    if not os.path.exists(RESULTS_DIR): os.makedirs(RESULTS_DIR)
    model = YOLO(MODEL_PATH)
    sample_images = list(SAMPLES_DIR.glob("*.jpg"))

    for img_path in sample_images:
        print(f"\n--- Rectificando Tablero: {img_path.name} ---")
        img = cv2.imread(str(img_path))
        if img is None: continue
        
        # 1. Detección YOLO
        results = model.predict(source=img, conf=0.4, save=False)
        
        all_pawns = []
        corners = {} # a1, h1, a8, h8

        for r in results:
            for box in r.boxes:
                cls_name = model.names[int(box.cls[0])]
                coords = box.xyxy[0].tolist()
                cx, cy = int((coords[0]+coords[2])/2), int((coords[1]+coords[3])/2)
                
                if cls_name == "white-pawn": all_pawns.append({"pos": [cx, cy], "color": "white", "used": False})
                elif cls_name == "black-pawn": all_pawns.append({"pos": [cx, cy], "color": "black", "used": False})
                elif cls_name == "white-rook": corners["a1"] = [cx, cy]
                elif cls_name == "white-knight": corners["h1"] = [cx, cy]
                elif cls_name == "black-rook": corners["a8"] = [cx, cy]
                elif cls_name == "black-knight": corners["h8"] = [cx, cy]

        # 2. Identificación Lógica de Puntos
        final_points = corners.copy()
        pawn_targets = {"white": {"b2": corners.get("a1"), "g2": corners.get("h1")},
                        "black": {"b7": corners.get("a8"), "g7": corners.get("h8")}}

        for color, targets in pawn_targets.items():
            for target_label, ref_corner in targets.items():
                if ref_corner is None: continue
                best_pawn = None
                min_dist = float('inf')
                for p in all_pawns:
                    if p["color"] == color and not p["used"]:
                        d = get_distance(p["pos"], ref_corner)
                        if d < min_dist:
                            min_dist = d
                            best_pawn = p
                if best_pawn:
                    final_points[target_label] = best_pawn["pos"]
                    best_pawn["used"] = True

        # Paso extra de asignación exhaustiva
        if len(all_pawns) == 4:
            unused_pawns = [p for p in all_pawns if not p["used"]]
            missing_labels = [l for l in ["b2", "g2", "b7", "g7"] if l not in final_points]
            if len(unused_pawns) == 1 and len(missing_labels) == 1:
                final_points[missing_labels[0]] = unused_pawns[0]["pos"]

        # 3. Cálculo de Homografía y Warp
        if len(final_points) >= 4:
            src_pts = []
            dst_pts = []
            for key, val in final_points.items():
                if key in IDEAL_CENTERS:
                    src_pts.append(val)
                    dst_pts.append(IDEAL_CENTERS[key])
            
            src_pts = np.array(src_pts, dtype=np.float32)
            dst_pts = np.array(dst_pts, dtype=np.float32)

            # Matriz de Homografía
            H, _ = cv2.findHomography(src_pts, dst_pts)
            if H is not None:
                # Warp Perspective para obtener el tablero de 800x800
                warped_img = cv2.warpPerspective(img, H, (800, 800))
                
                # Guardar el tablero rectificado
                output_path = RESULTS_DIR / f"warped_{img_path.name}"
                cv2.imwrite(str(output_path), warped_img)
                print(f"Tablero rectificado guardado: {output_path.name} (Usando {len(src_pts)} puntos)")
            else:
                print(f"Error: Falló el cálculo de Homografía para {img_path.name}")
        else:
            print(f"Error: Insuficientes puntos para homografía ({len(final_points)}) en {img_path.name}")

if __name__ == "__main__":
    main()
