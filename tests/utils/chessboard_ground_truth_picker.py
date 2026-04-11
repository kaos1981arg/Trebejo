from typing import Any

import cv2
import numpy as np
import json
from pathlib import Path
import os

# --- Configuración ---
# Directorio donde se guardarán los JSON de ground truth
GROUND_TRUTH_DIR = Path(__file__).resolve().parent.parent / "tests" / "data" / "board"
# Directorio de las imágenes a etiquetar
IMAGES_DIR = Path(__file__).resolve().parent.parent / "tests" / "data" / "board"

# Nombres de las casillas en orden (a1, b1, ..., h8)
SQUARE_NAMES = [
    f"{chr(ord('a') + col)}{row}" for row in range(1, 9) for col in range(8)
]
SQUARE_NAMES.reverse()  # Para que empiece en a8 y termine en h1 (o viceversa, ajusta según tu preferencia)
# Ajustamos el orden para que sea a1, b1, c1... h1, a2, b2... h8
SQUARE_NAMES_FLAT = []
for row in range(1, 9):
    for col in range(8):
        SQUARE_NAMES_FLAT.append(f"{chr(ord('a') + col)}{row}")

# --- Variables Globales ---
clicked_points: dict[str, list[int]] = {}
current_image: np.ndarray | None = None
current_image_name: str = ""
current_square_index: int = 0


def mouse_callback(event: Any, x: int, y: int, _flags: Any, _param: Any) -> None:
    global clicked_points, current_square_index, current_image, current_image_name

    if event == cv2.EVENT_LBUTTONDOWN:
        square_name = SQUARE_NAMES_FLAT[current_square_index]
        clicked_points[square_name] = [x, y]
        print(f"Punto para {square_name}: ({x}, {y})")

        # Dibujar el punto y la etiqueta
        cv2.circle(current_image, (x, y), 5, (0, 255, 0), -1)  # Verde
        cv2.putText(
            current_image,
            square_name,
            (x + 10, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        cv2.imshow("Image Picker", current_image)

        current_square_index += 1
        if current_square_index < len(SQUARE_NAMES_FLAT):
            print(
                f"Haz clic en el centro de la casilla: {SQUARE_NAMES_FLAT[current_square_index]}"
            )
        else:
            print("\n¡Todos los puntos han sido seleccionados!")
            save_ground_truth()
            cv2.destroyAllWindows()


def save_ground_truth() -> None:
    global clicked_points, current_image_name

    if not GROUND_TRUTH_DIR.exists():
        os.makedirs(GROUND_TRUTH_DIR)

    output_file = GROUND_TRUTH_DIR / f"{current_image_name}.json"
    with open(output_file, "w") as f:
        json.dump(
            {"image_name": current_image_name, "squares": clicked_points}, f, indent=4
        )
    print(f"Ground truth guardado en: {output_file}")


def main() -> None:
    global clicked_points, current_image, current_image_name, current_square_index

    if not IMAGES_DIR.exists():
        print(f"Error: El directorio de imágenes {IMAGES_DIR} no existe.")
        return

    # Buscar imágenes
    image_files = list(IMAGES_DIR.glob("*.jpg"))
    if not image_files:
        print(f"No se encontraron imágenes 'warped_*.jpg' en {IMAGES_DIR}.")
        return

    print("--- Selector de Puntos de Ground Truth para Tablero ---")
    print("Haz clic en el centro de cada casilla en el orden indicado.")
    print("Presiona 'q' para salir en cualquier momento.")

    for img_path in image_files:
        current_image_name = img_path.stem  # Nombre del archivo sin extensión
        current_image = cv2.imread(str(img_path))
        if current_image is None:
            print(f"Error: No se pudo cargar la imagen {img_path}")
            continue

        clicked_points = {}
        current_square_index = 0

        cv2.namedWindow("Image Picker", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Image Picker", mouse_callback)

        print(f"\nCargando imagen: {current_image_name}.jpg")
        print(
            f"Haz clic en el centro de la casilla: {SQUARE_NAMES_FLAT[current_square_index]}"
        )
        cv2.imshow("Image Picker", current_image)

        key = cv2.waitKey(0)
        if key == ord("q"):
            break

        # Si se completaron todos los puntos, save_ground_truth ya se llamó
        # Si se salió con 'q' antes de terminar, no guardamos
        if current_square_index < len(SQUARE_NAMES_FLAT):
            print("Selección de puntos interrumpida.")
        else:
            print(f"Puntos para {current_image_name} completados.")

    print("\nProceso finalizado.")


if __name__ == "__main__":
    main()
