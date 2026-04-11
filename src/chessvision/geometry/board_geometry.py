class BoardGeometry:
    def __init__(self, board_size: int, border_size: int):
        self.board_size = board_size
        self.square_size = self.board_size // 8
        self.border_size = border_size

    def get_ideal_square_center(self, square: str) -> tuple[int, int]:
        col = ord(square[0]) - ord("a")
        row = int(square[1]) - 1
        return (
            col * self.square_size + self.square_size // 2 + self.border_size,
            row * self.square_size + self.square_size // 2 + self.border_size,
        )
