from src.chessvision.geometry import BoardGeometry


def test_reject_collinear_points() -> None:
    """Verifica que se rechacen puntos que están alineados (homografía inestable)."""
    geometry = BoardGeometry()
    # 4 puntos en una línea casi perfecta
    collinear_points = {
        "a1": [100, 100],
        "b2": [200, 200],
        "c3": [300, 300],
        "d4": [400, 400],
        "e5": [1500, 1500],
    }
    h = geometry.calculate_homography(collinear_points)
    assert h is None, "Debería rechazar puntos colineales"


def test_accept_distributed_points() -> None:
    """Verifica que se acepten puntos bien distribuidos en el tablero."""
    geometry = BoardGeometry()
    # Puntos en las 4 esquinas del tablero (escenario ideal)
    distributed_points = {
        "a1": [100, 100],
        "h1": [100, 1500],
        "a8": [1500, 100],
        "h8": [1500, 1500],
        "e5": [900, 900],
    }
    h = geometry.calculate_homography(distributed_points)
    assert h is not None, "Debería aceptar puntos bien distribuidos"


def test_minimum_points_requirement() -> None:
    """Verifica que necesite al menos 5 puntos."""
    geometry = BoardGeometry()
    few_points = {
        "a1": [100, 100],
        "h1": [100, 1700],
        "a8": [1700, 100],
        "h8": [1700, 1700],
    }
    h = geometry.calculate_homography(few_points)
    assert h is None, "Necesita al menos 5 puntos para una homografía"
