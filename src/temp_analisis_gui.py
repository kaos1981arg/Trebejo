import flet as ft

# Intentamos importar los estilos si están disponibles, si no usamos valores por defecto
try:
    from views.styles import COLOR_PANEL, COLOR_ACCENT
except ImportError:
    COLOR_PANEL = "#1a1a1a"
    COLOR_ACCENT = "#d4af37"


def main(page: ft.Page) -> None:
    page.title = "Gabinete de Análisis Táctico - Prototipo"
    page.bgcolor = COLOR_PANEL
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1100
    page.window.height = 850
    page.padding = 20
    page.scroll = ft.ScrollMode.ADAPTIVE

    # --- CABECERA ---
    header = ft.Row(
        [
            ft.Icon(ft.Icons.ANALYTICS, color=COLOR_ACCENT, size=40),
            ft.Text(
                "Gabinete de Análisis Táctico",
                size=32,
                color=COLOR_ACCENT,
                weight=ft.FontWeight.BOLD,
                font_family="Georgia",
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # --- TABLERO (Simulado con un GridView por ahora) ---
    # En el futuro aquí irá un componente de tablero real (python-chess + flet)
    def create_square(color: ft.Colors, label: str = "") -> ft.Container:
        return ft.Container(
            content=ft.Text(
                label,
                color=(
                    ft.Colors.BLACK54
                    if color == ft.Colors.BROWN_100
                    else ft.Colors.WHITE54
                ),
            ),
            bgcolor=color,
            width=60,
            height=60,
            alignment=ft.Alignment.CENTER,
        )

    squares = []
    for r in range(8):
        for c in range(8):
            color = ft.Colors.BROWN_100 if (r + c) % 2 == 0 else ft.Colors.BROWN_700
            squares.append(create_square(color))

    tablero_grid = ft.Container(
        content=ft.GridView(
            runs_count=8,
            max_extent=70,
            child_aspect_ratio=1.0,
            spacing=0,
            run_spacing=0,
            controls=squares,
        ),
        width=560,
        height=560,
        border=ft.Border.all(5, COLOR_ACCENT),
        border_radius=5,
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK),
    )

    # --- CONTROLES DE REPRODUCCIÓN ---
    controles = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    ft.Icons.KEYBOARD_DOUBLE_ARROW_LEFT_ROUNDED,
                    icon_color=COLOR_ACCENT,
                    icon_size=30,
                    tooltip="Inicio",
                ),
                ft.IconButton(
                    ft.Icons.KEYBOARD_ARROW_LEFT_ROUNDED,
                    icon_color=COLOR_ACCENT,
                    icon_size=35,
                    tooltip="Anterior",
                ),
                ft.IconButton(
                    ft.Icons.PLAY_CIRCLE_FILL_ROUNDED,
                    icon_color=COLOR_ACCENT,
                    icon_size=50,
                    tooltip="Reproducir",
                ),
                ft.IconButton(
                    ft.Icons.KEYBOARD_ARROW_RIGHT_ROUNDED,
                    icon_color=COLOR_ACCENT,
                    icon_size=35,
                    tooltip="Siguiente",
                ),
                ft.IconButton(
                    ft.Icons.KEYBOARD_DOUBLE_ARROW_RIGHT_ROUNDED,
                    icon_color=COLOR_ACCENT,
                    icon_size=30,
                    tooltip="Final",
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        margin=ft.Margin.only(top=10),
    )

    # --- PANEL LATERAL (Anotación y Motor) ---
    panel_lateral = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "ANÁLISIS EN TIEMPO REAL",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_ACCENT,
                ),
                ft.Divider(color=COLOR_ACCENT, thickness=1),
                # Barra de Evaluación (Simulada)
                ft.Row(
                    [
                        ft.Text("Evaluación: +0.85", color=ft.Colors.WHITE70),
                        ft.Icon(
                            ft.Icons.TRENDING_UP, color=ft.Colors.GREEN_400, size=16
                        ),
                    ]
                ),
                ft.ProgressBar(
                    value=0.55, color=COLOR_ACCENT, bgcolor=ft.Colors.BLACK26, height=10
                ),
                ft.Divider(color=ft.Colors.TRANSPARENT, height=10),
                # Lista de movimientos (PGN)
                ft.Text(
                    "MOVIMIENTOS (PGN)",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_ACCENT,
                ),
                ft.Container(
                    content=ft.ListView(
                        controls=[
                            ft.Text("1. e4   e5", size=16, font_family="monospace"),
                            ft.Text("2. Nf3  Nc6", size=16, font_family="monospace"),
                            ft.Text(
                                "3. Bb5  a6",
                                size=16,
                                font_family="monospace",
                                weight=ft.FontWeight.BOLD,
                                bgcolor=ft.Colors.WHITE10,
                            ),
                            ft.Text("4. Ba4  Nf6", size=16, font_family="monospace"),
                            ft.Text("5. O-O  Be7", size=16, font_family="monospace"),
                        ],
                        spacing=5,
                    ),
                    expand=True,
                    bgcolor=ft.Colors.BLACK26,
                    padding=15,
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.WHITE10),
                ),
                # Botones de Acción
                ft.Column(
                    [
                        ft.ElevatedButton(
                            "Importar PGN",
                            icon=ft.Icons.FILE_UPLOAD,
                            width=float("inf"),
                        ),
                        ft.ElevatedButton(
                            "Exportar Análisis",
                            icon=ft.Icons.FILE_DOWNLOAD,
                            width=float("inf"),
                        ),
                        ft.OutlinedButton(
                            "Volver al Menú",
                            icon=ft.Icons.ARROW_BACK,
                            width=float("inf"),
                            on_click=lambda _: print("Navegando a home..."),
                        ),
                    ],
                    spacing=10,
                ),
            ],
            spacing=15,
            expand=True,
        ),
        width=350,
        height=650,
        padding=25,
        bgcolor=ft.Colors.with_opacity(0.05, COLOR_ACCENT),
        border_radius=15,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, COLOR_ACCENT)),
    )

    # --- CUERPO PRINCIPAL ---
    body = ft.Row(
        [
            ft.Column(
                [tablero_grid, controles],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            ft.VerticalDivider(width=20, color=ft.Colors.TRANSPARENT),
            panel_lateral,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Agregar todo a la página
    page.add(header, ft.Divider(height=30, color=ft.Colors.TRANSPARENT), body)


if __name__ == "__main__":
    # Importante: assets_dir="../assets" para que encuentre las imágenes si las usamos
    ft.run(main=main, assets_dir="../assets")
