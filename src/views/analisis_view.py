import flet as ft
from .styles import COLOR_PANEL, COLOR_ACCENT

class AnalisisView(ft.View):
    def __init__(self, page_ref: ft.Page):
        self.main_page = page_ref
        super().__init__(
            route='/analisis',
            bgcolor=COLOR_PANEL,
            scroll=ft.ScrollMode.ADAPTIVE,
            appbar=ft.AppBar(
                title=ft.Text("Gabinete de Análisis Táctico", color=COLOR_ACCENT),
                bgcolor=COLOR_PANEL,
                center_title=True,
                color=COLOR_ACCENT
            ),
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Gabinete de Análisis Táctico",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_ACCENT),
                        ft.Text("Aquí se analizarán las partidas.",
                                size=16,
                                color=COLOR_ACCENT),
                        ft.ElevatedButton("Volver", on_click=lambda _: self.main_page.go("/"))
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ]
        )
