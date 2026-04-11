import json
import random
from pathlib import Path

import cv2
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from src.chessvision.geometry import BoardGeometry
from scipy.signal import find_peaks

DATA_DIR = Path("C:/Users/usuario/PycharmProjects/Trebejo/tests/data/board/")


def draw_master_lines(original_image, master_lines, color=(0, 255, 0), thickness=2):
    """
    Dibuja líneas infinitas en una imagen dada sus parámetros polares (rho, theta).

    Args:
        imagen_original: La imagen sobre la que dibujar (se hará una copia).
        lineas_maestras: Lista o array de [rho, theta] (retornado por get_master_lines).
        color: Tupla BGR del color de la línea.
        grosor: Grosor de la línea en píxeles.

    Returns:
        Imagen con las líneas dibujadas.
    """
    imagen_con_lineas = original_image.copy()

    # Asegurarnos de que tenemos las dimensiones para los puntos extremos
    alto, ancho = imagen_con_lineas.shape[:2]
    longitud_maxima = (
        max(alto, ancho) * 2
    )  # Un factor de seguridad para asegurar que cruza toda la imagen

    for rho, theta in master_lines:
        # 1. Calcular funciones trigonométricas (theta debe estar en radianes)
        a = np.cos(theta)
        b = np.sin(theta)

        # 2. Calcular el punto (x0, y0) que es el punto más cercano de la línea al origen
        x0 = a * rho
        y0 = b * rho

        # 3. Calcular el vector director de la línea.
        # Si el vector perpendicular es (a, b), el vector director es (-b, a)
        # Multiplicamos por la longitud máxima para obtener puntos lejanos
        x1 = int(x0 + longitud_maxima * (-b))
        y1 = int(y0 + longitud_maxima * (a))
        x2 = int(x0 - longitud_maxima * (-b))
        y2 = int(y0 - longitud_maxima * (a))

        # 4. Dibujar el segmento entre los puntos calculados
        cv2.line(imagen_con_lineas, (x1, y1), (x2, y2), color, thickness, cv2.LINE_AA)

    return imagen_con_lineas


def polar_params_line(x1: int, y1: int, x2: int, y2: int) -> tuple[float, float]:
    """
    Calcula los parámetros polares (rho, theta) de una línea dados dos puntos (x1, y1) y (x2, y2).
    """
    # Calcular el ángulo de la línea con respecto al eje X
    angle = np.arctan2(y2 - y1, x2 - x1) + np.pi / 2

    # Normalizar el ángulo para que esté en el rango [0, pi)
    # Esto es importante para que líneas con la misma orientación pero diferentes direcciones
    # tengan el mismo theta.
    theta = angle % np.pi

    if angle < 0:
        angle += np.pi

    # Calcular rho (distancia perpendicular al origen)
    rho = x1 * np.cos(theta) + y1 * np.sin(theta)

    return rho, theta


def get_master_lines(lines: list, k: int = 18) -> np.ndarray:
    parameters = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        parameters.append(polar_params_line(x1, y1, x2, y2))

    parameters_arr = np.array(parameters, dtype=np.float32)

    # K-Means para encontrar las K líneas principales
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.01)
    _, _, centers = cv2.kmeans(
        parameters_arr,
        k,
        bestLabels=None,
        criteria=criteria,
        attempts=20,
        flags=cv2.KMEANS_PP_CENTERS,
    )

    return centers  # Devuelve lista de [rho_master, theta_master]


def get_board_lines(lines: list) -> list:
    output_lines = []

    theta_mean = np.mean([line[1] for line in lines])
    print(f"DEBUG: Theta promedio: {theta_mean * 180 / np.pi}")

    return output_lines


def calc_cluster_mean_params(
    lines_arr: np.ndarray, clean_label: np.ndarray
) -> dict[int, tuple[float, float]]:
    """
    Calcula la media de los parámetros polares (rho, theta) para un grupo de líneas.
    """
    print(f"DEBUG: lines_arr: {lines_arr}")
    unique_labels = np.unique(clean_label)
    print(f"DEBUG: unique_labels: {unique_labels}")

    grouped_index = {}
    for l in unique_labels:
        indices = np.where(clean_label == l)[0]
        grouped_index[l] = indices

    group_mean = {}
    for group, index in grouped_index.items():
        rho_real = np.mean([lines_arr[idx][0] for idx in index])
        theta_real = np.mean([lines_arr[idx][1] for idx in index])
        group_mean[group] = [rho_real, theta_real]

    print(f"DEBUG: group_mean: {group_mean}")

    return group_mean


def cluster_lines(lines_params: list[tuple]) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()

    lines_arr = np.array(lines_params, dtype=np.float32)
    lines_scaled = scaler.fit_transform(lines_arr)

    db = DBSCAN(eps=0.3, min_samples=3).fit(lines_scaled)

    mask = db.labels_ >= 0
    clean_lines = np.array(lines_arr)[mask]
    clean_label = db.labels_[mask]

    return clean_lines, clean_label


def rot_corr(img: np.ndarray) -> np.ndarray:
    # Obtener dimensiones y centro
    h, w = img.shape[:2]
    centro = (w // 2, h // 2)

    # Determinar el ángulo de rotación
    # 1. Preparar la imagen
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 100, apertureSize=3)

    # 2. Detectar líneas con HoughLinesP
    # threshold: mínimo de intersecciones; minLineLength: longitud mínima de línea
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, threshold=100, minLineLength=80, maxLineGap=600
    )

    if lines is None:
        return img

    # Agrupar líneas por orientación (horizontales y verticales)
    hor_lines = []
    ver_lines = []

    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Calcular ángulo
        angulo = np.arctan2(y2 - y1, x2 - x1)
        # Normalizar: Queremos saber cuánto se desvía de 0 o 90 grados
        # El ajuste depende de si la línea es más horizontal o vertical
        if angulo < 0:
            angulo += np.pi

        if angulo > np.pi / 2:
            angulo -= np.pi

        if abs(angulo) < np.pi / 4:  # Horizontal
            hor_lines.append(line)
        elif abs(angulo) > np.pi / 4:  # Vertical
            ver_lines.append(line)

    hor_lines_k = get_master_lines(hor_lines, k=11)
    img_1 = draw_master_lines(img, hor_lines_k)
    ver_lines_k = get_master_lines(ver_lines, k=11)
    img_1 = draw_master_lines(img_1, ver_lines_k, color=(0, 0, 255))

    img_rezised = cv2.resize(img_1, (600, 600))
    img_ed_rezised = cv2.resize(edges, (600, 600))
    cv2.imshow("Warped Image", img_rezised)
    cv2.imshow("Warped Image Edges", img_ed_rezised)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    hor_lines_params = [polar_params_line(*line[0]) for line in hor_lines]
    clean_hor_lines, clean_hor_label = cluster_lines(hor_lines_params)
    master_hor_lines = list(
        calc_cluster_mean_params(clean_hor_lines, clean_hor_label).values()
    )

    ver_lines_params = [polar_params_line(*line[0]) for line in ver_lines]
    clean_ver_lines, clean_ver_label = cluster_lines(ver_lines_params)
    master_ver_lines = list(
        calc_cluster_mean_params(clean_ver_lines, clean_ver_label).values()
    )

    img_2 = draw_master_lines(img, master_hor_lines)
    img_2 = draw_master_lines(img_2, master_ver_lines, color=(0, 0, 255))
    img_rezised = cv2.resize(img_2, (600, 600))
    cv2.imshow("Cleaned Lines", img_rezised)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    angulos_corregidos = []

    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Calcular ángulo en grados
        angulo = np.degrees(np.arctan2(y2 - y1, x2 - x1))

        # Normalizar: Queremos saber cuánto se desvía de 0 o 90 grados
        # El ajuste depende de si la línea es más horizontal o vertical
        if angulo < 0:
            angulo += 180

        # Esto "colapsa" las líneas verticales sobre las horizontales
        desviacion = (angulo + 45) % 90 - 45
        angulos_corregidos.append(desviacion)

    # La mediana nos da la rotación necesaria para enderezar
    angulo_rotacion = np.median(angulos_corregidos)

    # Matriz de rotación
    M = cv2.getRotationMatrix2D(centro, angulo_rotacion, 1.0)

    # Aplicar la rotación
    img_rotada = cv2.warpAffine(
        img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )

    return img_rotada


def graph_profiles(
    img: np.ndarray, row_profile: np.ndarray, col_profile: np.ndarray
) -> None:
    # Dimensiones de la imagen
    h, w = img.shape[:2]
    margin = 100  # Margen para los gráficos

    # Crear lienzo nuevo (Imagen + márgenes)
    canvas = np.zeros((h + margin, w + margin, 3), dtype="uint8")
    # Colocar la imagen original en la esquina inferior derecha
    canvas[margin:, margin:] = img

    # --- Graficar Perfil de Columnas (Arriba) ---
    # Normalizar a 0-100 (altura del margen)
    col_norm = (col_profile / 255.0) * margin
    points_col = []
    for x in range(w):
        # Punto (x + margen, margen - valor_perfil)
        points_col.append([x + margin, int(margin - col_norm[x])])

    cv2.polylines(canvas, [np.array(points_col)], False, (0, 255, 255), 1)

    # --- Graficar Perfil de Filas (Izquierda) ---
    # Normalizar a 0-100 (ancho del margen)
    row_norm = (row_profile / 255.0) * margin
    points_row = []
    for y in range(h):
        # Punto (margen - valor_perfil, y + margen)
        points_row.append([int(margin - row_norm[y]), y + margin])

    cv2.polylines(canvas, [np.array(points_row)], False, (255, 0, 255), 1)

    img_rezised = cv2.resize(canvas, (600, 600))
    cv2.imshow("Warped Image", img_rezised)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def grig_analyzer(img: np.ndarray) -> None:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    row_profile = np.mean(gray, axis=1)
    col_profile = np.mean(gray, axis=0)

    graph_profiles(img, row_profile, col_profile)

    peaks_h, _ = find_peaks(-col_profile, distance=80, prominence=4)
    peaks_v, _ = find_peaks(-row_profile, distance=80, prominence=4)

    print(f"DEBUG: Líneas Verticales: {len(peaks_h)}, Horizontales: {len(peaks_v)}")
    print(f"DEBUG: Líneas Verticales: {peaks_h}, Horizontales: {peaks_v}")

    # Dibujar lineas horizontales
    for peak in peaks_h:
        cv2.line(img, (0, peak), (img.shape[1], peak), (0, 0, 255), 5)

    # Dibujar lineas verticales
    for peak in peaks_v:
        cv2.line(img, (peak, 0), (peak, img.shape[0]), (0, 0, 255), 5)

    img_rezised = cv2.resize(img, (600, 600))
    cv2.imshow("Warped Image", img_rezised)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main(image_name: str, iteration: int) -> None:
    random.seed(iteration + 42)
    np.random.seed(iteration + 42)

    original_image_path = DATA_DIR / f"{image_name}.jpg"
    original_img = cv2.imread(str(original_image_path))

    with open(DATA_DIR / f"{image_name}.json", "r") as f:
        gt_data = json.load(f)

    geometry_engine = BoardGeometry()
    all_squares = list(gt_data["squares"].keys())

    # 1. Seleccionar un conjunto aleatorio de casillas (entre 4 y 12) de las 64 posibles
    num_refs = random.randint(5, 12)
    selected_refs = random.sample(all_squares, num_refs)

    print(selected_refs)

    noisy_points = {}
    noise_level = 15  # Ruido agresivo para forzar el fallo sin refinamiento

    for ref in selected_refs:
        orig_p = gt_data["squares"][ref]
        noisy_p = [
            orig_p[0] + random.randint(-noise_level, noise_level),
            orig_p[1] + random.randint(-noise_level, noise_level),
        ]
        noisy_points[ref] = noisy_p

    for ref, point in noisy_points.items():
        cv2.circle(
            img=original_img,
            center=point,
            radius=10,
            color=(0, 0, 255),
            thickness=5,
        )

    img_rezised = cv2.resize(original_img, (800, 600))
    cv2.imshow("Original Image", img_rezised)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 2. Calcular homografía inicial con ruido
    h_initial = geometry_engine.calculate_homography(noisy_points)

    # 3. Rectificar imagen
    if h_initial is None:
        return

    warped_img = geometry_engine.rectify_image(original_img, h_initial)

    img_rezised = cv2.resize(warped_img, (600, 600))
    cv2.imshow("Warped Image", img_rezised)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    _rot_warped_img = rot_corr(warped_img)
    # grig_analyzer(warped_img)


if __name__ == "__main__":
    test_scenarios = []
    if DATA_DIR.exists():
        image_names = [f.stem for f in DATA_DIR.glob("*.json")]
        for name in image_names:
            for i in range(1):  # 5 intentos aleatorios por imagen
                test_scenarios.append((name, i))

    for image_name, iteration in test_scenarios:
        main(image_name, iteration)
