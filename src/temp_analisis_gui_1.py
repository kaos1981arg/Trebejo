import flet as ft
import chess
import chess.svg

from views.styles import COLOR_PANEL, COLOR_ACCENT


def main(page: ft.Page) -> None:
    page.title = "Trebejo - Gabinete de Análisis Táctico - Prototipo"
    page.bgcolor = COLOR_PANEL

    # Appbar
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.NAVIGATE_BEFORE),
        title=ft.Text("Trebejo - Gabinete de Análisis Táctico"),
        bgcolor=COLOR_PANEL,
        center_title=True,
        color=COLOR_ACCENT,
    )

    # --- CABECERA Entrada FEN y PGN ---
    input_fen = ft.Row(
        controls=[
            ft.Text("FEN:", color=COLOR_ACCENT),
            ft.TextField(
                expand=True,
                text_align=ft.TextAlign.LEFT,
                content_padding=8,
                dense=True,
                border_radius=5,
                border_color=COLOR_ACCENT,
                cursor_color=COLOR_ACCENT,
                selection_color=COLOR_ACCENT,
                text_style=ft.TextStyle(color=COLOR_ACCENT),
            ),
        ]
    )  # Cierre de ft.Row
    input_pgn = ft.Row(
        controls=[
            ft.Text("PGN:", color=COLOR_ACCENT),
            ft.TextField(
                expand=True,
                text_align=ft.TextAlign.LEFT,
                content_padding=8,
                dense=True,
                border_radius=5,
                border_color=COLOR_ACCENT,
                cursor_color=COLOR_ACCENT,
                selection_color=COLOR_ACCENT,
                text_style=ft.TextStyle(color=COLOR_ACCENT),
                multiline=True,
                min_lines=3,
                max_lines=6,
            ),
        ]
    )

    input_data = ft.Column(controls=[input_fen, input_pgn])  # Cierre de ft.Column

    # --- TABLERO ---
    board = chess.Board()
    board_svg = chess.svg.board(board, size=350)
    board_image = ft.Image(src=board_svg, fit=ft.BoxFit.CONTAIN)
    board_container = ft.Container(
        content=board_image, expand=True, alignment=ft.Alignment.CENTER
    )

    page.add(input_data, board_container)

    page.update()


if __name__ == "__main__":
    ft.run(main=main)
