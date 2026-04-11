import pytest
import json
from pathlib import Path
import cv2
import numpy as np
import sys
import os
import random

# Asegurar que el directorio 'src' esté en el path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)
from chessvision.geometry import BoardGeometry

DATA_DIR = Path(__file__).parent.parent / "data" / "board"


def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# Parámetros para el test: generamos 5 iteraciones por cada imagen de ground truth
test_scenarios = []
if DATA_DIR.exists():
    image_names = [f.stem for f in DATA_DIR.glob("*.json")]
    for name in image_names:
        for i in range(5):  # 5 intentos aleatorios por imagen
            test_scenarios.append((name, i))


@pytest.mark.parametrize("image_name, iteration", test_scenarios)
def test_board_geometry_robustness(image_name, iteration):
    # Semilla variable pero predecible por iteración para debugging
    random.seed(iteration + 42)
    np.random.seed(iteration + 42)

    original_image_path = DATA_DIR / f"{image_name}.jpg"
    original_img = cv2.imread(str(original_image_path))

    with open(DATA_DIR / f"{image_name}.json", "r") as f:
        gt_data = json.load(f)

    geometry_engine = BoardGeometry()
    all_squares = list(gt_data["squares"].keys())

    # 1. Seleccionar un conjunto aleatorio de casillas (entre 4 y 12) de las 64 posibles
    num_refs = random.randint(4, 12)
    selected_refs = random.sample(all_squares, num_refs)

    noisy_points = {}
    noise_level = 15  # Ruido agresivo para forzar el fallo sin refinamiento

    for ref in selected_refs:
        orig_p = gt_data["squares"][ref]
        noisy_p = [
            orig_p[0] + random.randint(-noise_level, noise_level),
            orig_p[1] + random.randint(-noise_level, noise_level),
        ]
        noisy_points[ref] = noisy_p

    # 2. Calcular homografía inicial con ruido
    H_initial = geometry_engine.calculate_homography(noisy_points)
    assert H_initial is not None

    # 3. Rectificar imagen
    warped_img = geometry_engine.rectify_image(original_img, H_initial)

    # 4. REFINAMIENTO (Lógica de valles de intensidad)
    # Aquí es donde debe ocurrir la magia para corregir el ruido de 25px
    final_aligned_img, H_refinement = geometry_engine.refine_alignment(warped_img)

    # 5. Validar precisión final sobre las 64 casillas
    H_final = H_refinement @ H_initial

    errors = []
    for square_name, original_coords in gt_data["squares"].items():
        ideal_coords = geometry_engine.ideal_centers[square_name]
        projected_coords = geometry_engine.transform_point(original_coords, H_final)
        errors.append(euclidean_distance(projected_coords, ideal_coords))

    avg_error = np.mean(errors)
    max_error = np.max(errors)

    print(f"\n--- [{image_name}] Iteración {iteration} ({num_refs} piezas) ---")
    print(f"  Error Medio: {avg_error:.2f} px")
    print(f"  Error Máximo: {max_error:.2f} px")

    # Aserciones: El refinamiento debe bajar el error medio a < 5px
    assert (
        avg_error < 5.0
    ), f"Error medio ({avg_error:.2f} px) demasiado alto. Refinamiento fallido."
    assert max_error < 15.0, f"Error máximo ({max_error:.2f} px) demasiado alto."
