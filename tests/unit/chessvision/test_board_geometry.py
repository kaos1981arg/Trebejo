import pytest
from src.chessvision.geometry import BoardGeometry


@pytest.fixture
def board_geometry_instance() -> BoardGeometry:
    board_size = 800
    border_size = 100
    return BoardGeometry(board_size, border_size)


test_scenarios = [
    ("a1", (150, 150)),
    ("a4", (150, 450)),
    ("b7", (250, 750)),
    ("g5", (750, 550)),
    ("h8", (850, 850)),
]


@pytest.mark.parametrize("square, expected_center", test_scenarios)
def test_get_ideal_square_center(
    board_geometry_instance: BoardGeometry,
    square: str,
    expected_center: tuple[int, int],
) -> None:
    """
    Tests that the ideal center for each square is calculated correctly.
    Calculation: border_size + (index * square_size) + square_size / 2
    With 800px board and 100px border: 100 + (index * 100) + 50
    """
    actual_center = board_geometry_instance.get_ideal_square_center(square)
    assert actual_center == (
        expected_center[0],
        expected_center[1],
    ), f"Center for {square} is incorrect."
