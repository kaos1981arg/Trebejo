import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.signal import find_peaks


class BoardGeometry:
    """
    Motor geométrico para la rectificación y alineación del tablero de ajedrez.
    """

    def __init__(self, target_size: int = 1000):
        self.target_size = target_size
        self.square_size = target_size // 10

        self.ideal_centers = {}
        for row in range(8):
            for col in range(8):
                name = f"{chr(ord('a') + col)}{row + 1}"
                self.ideal_centers[name] = [
                    (col + 1) * self.square_size + self.square_size // 2,
                    (7 - row + 1) * self.square_size + self.square_size // 2,
                ]

    def calculate_homography(
        self, detected_points: Dict[str, List[int]]
    ) -> Optional[np.ndarray]:
        """
        Calcula y valida la matriz de homografía inicial.
        Usa Determinante y RMSE para asegurar una transformación estable.
        """
        src_pts, dst_pts = [], []
        for name, pos in detected_points.items():
            if name in self.ideal_centers:
                src_pts.append(pos)
                dst_pts.append(self.ideal_centers[name])

        if len(src_pts) < 5:
            return None

        src_pts_arr = np.array(src_pts, dtype=np.float32)
        dst_pts_arr = np.array(dst_pts, dtype=np.float32)

        matrix_h, mask = cv2.findHomography(
            srcPoints=src_pts_arr,
            dstPoints=dst_pts_arr,
            method=cv2.RANSAC,
            ransacReprojThreshold=15,
        )
        inliers = np.sum(mask)
        print(f"DEBUG: inliers: {inliers}")
        if matrix_h is None or inliers < 4:
            return None

        # --- VALIDACIÓN 1: Determinante ---
        # Una homografía válida para un tablero real debe tener un determinante significativamente
        # diferente de cero y positivo (para mantener la orientación horaria/antihoraria).
        det = np.linalg.det(matrix_h)
        print(f"DEBUG: Determinante de la Homografía: {det:.2e}")
        if abs(det) < 1e-9 or det < 0:
            print(f"DEBUG: Homografía rechazada por determinante inválido ({det:.2e})")
            return None

        # --- VALIDACIÓN 2: Error de Reproyección (RMSE) ---
        # Proyectamos los puntos de origen y vemos qué tan lejos caen de sus destinos ideales.
        # cv2.perspectiveTransform espera una lista de puntos con forma (N, 1, 2)
        src_pts_reshaped = src_pts_arr.reshape(-1, 1, 2)
        projected_pts = cv2.perspectiveTransform(src_pts_reshaped, matrix_h)
        projected_pts = projected_pts.reshape(-1, 2)

        # Error medio (distancia euclidiana)
        distances = np.linalg.norm(dst_pts_arr - projected_pts, axis=1)
        rmse = np.mean(distances)
        print("DEBUG: Error de Reproyección (RMSE):", rmse, "px")

        # Si el error de los puntos que USAMOS para calcular es > 30px, la matriz es inestable
        if rmse > 30.0:
            print(f"DEBUG: Homografía rechazada por RMSE alto ({rmse:.2f} px)")
            return None

        return matrix_h

    def rectify_image(self, image: np.ndarray, matrix_h: np.ndarray) -> np.ndarray:
        """Aplica la transformación de perspectiva."""
        return cv2.warpPerspective(
            image, matrix_h, (self.target_size, self.target_size)
        )

    def _get_best_linear_fit(
        self, peaks: List[float]
    ) -> Tuple[Optional[float], Optional[float]]:
        if len(peaks) < 2:
            return None, None
        steps = np.diff(peaks)
        avg_step = np.mean(steps).item()
        starts = [p - (i + 1) * avg_step for i, p in enumerate(peaks)]
        avg_start = np.mean(starts).item()
        return avg_start, avg_step

    def refine_alignment(
        self, warped_image: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Refina la alineación usando valles de intensidad."""
        gray = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
        row_profile = np.mean(gray, axis=1)
        col_profile = np.mean(gray, axis=0)

        peaks_h, _ = find_peaks(
            -col_profile, distance=self.square_size * 0.8, prominence=3
        )
        peaks_v, _ = find_peaks(
            -row_profile, distance=self.square_size * 0.8, prominence=3
        )

        peaks_h = np.array([p for p in peaks_h if 40 < p < (self.target_size - 40)])
        peaks_v = np.array([p for p in peaks_v if 40 < p < (self.target_size - 40)])

        start_x, step_x = self._get_best_linear_fit(sorted(peaks_h))
        start_y, step_y = self._get_best_linear_fit(sorted(peaks_v))

        if (
            start_x is not None
            and start_y is not None
            and step_x is not None
            and step_y is not None
        ):
            x0, x8 = start_x, start_x + 8 * step_x
            y0, y8 = start_y, start_y + 8 * step_y
            src_pts = np.array(
                [[x0, y0], [x8, y0], [x8, y8], [x0, y8]], dtype=np.float32
            )
            dst_pts = np.array(
                [
                    [0, 0],
                    [self.target_size, 0],
                    [self.target_size, self.target_size],
                    [0, self.target_size],
                ],
                dtype=np.float32,
            )
            h_ref = cv2.getPerspectiveTransform(src_pts, dst_pts)
            aligned_img = cv2.warpPerspective(
                warped_image, h_ref, (self.target_size, self.target_size)
            )
            return aligned_img, h_ref

        return warped_image, np.eye(3)

    def transform_point(self, point: List[int], matrix_h: np.ndarray) -> List[int]:
        p = np.array([point[0], point[1], 1.0], dtype=np.float32)
        p_transformed = matrix_h @ p
        if p_transformed[2] != 0:
            p_transformed /= p_transformed[2]
        return [int(p_transformed[0]), int(p_transformed[1])]
