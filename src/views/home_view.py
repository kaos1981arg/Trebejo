import flet as ft
from .styles import COLOR_PANEL, COLOR_ACCENT
from components.custom_buttons import OptionButton

class HomeView(ft.View):
    def __init__(self, page_ref: ft.Page):
        self.main_page = page_ref
        super().__init__(route='/',
                         bgcolor=COLOR_PANEL,
                         scroll=ft.ScrollMode.ADAPTIVE,
                         # Appbar con el Logo Dorado Ornamental
                         appbar=ft.AppBar(title=ft.Image(src='logo_ornamental.png',
                                                         height=60,
                                                         fit=ft.BoxFit.CONTAIN
                                                         ),
                                          leading=ft.Icon(ft.Icons.MENU),
                                          bgcolor=COLOR_PANEL,
                                          center_title=True,
                                          color=COLOR_ACCENT
                                          ),
                         controls=[
                             # El Tablero de Portada
                             ft.Image(src='fondo_tablero.png',
                                            width=450,
                                            height=300,
                                            fit=ft.BoxFit.COVER
                                            ),
                             # Sección Opciones de Juego
                             ft.Column(controls= [ft.Text("Opciones de Juego",
                                                          size=18,
                                                          weight=ft.FontWeight.W_500,
                                                          color=COLOR_ACCENT
                                                          ),
                                                  OptionButton(title="Duelo de Autómatas IA",
                                                               subtitle="Enfréntate al cerebro mecánico",
                                                               icon_image="icon_steampunk_robot.png",
                                                               decor_image="texture_parchment.png",
                                                               on_click=self.handle_click,
                                                               data="/duelo"
                                                               ),
                                                  OptionButton(title="Red de Correspondencia Global",
                                                               subtitle="Compite a distancia en línea",
                                                               icon_image="icon_steampunk_beaker.png",
                                                               decor_image="texture_parchment.png",
                                                               on_click=self.handle_click,
                                                               data="/red"),
                                                  OptionButton(title="Gabinete de Análisis Táctico",
                                                               subtitle="Estudia con el motor de ajedrez",
                                                               icon_image="icon_steampunk_king.png",
                                                               decor_image="texture_parchment.png",
                                                               on_click=self.handle_click,
                                                               data="/analisis"
                                                               )
                                                  ]
                                       ),
                             # Sección Varios
                             ft.Column(controls=[ft.Text("Varios",
                                                         size=16,
                                                         weight=ft.FontWeight.W_500,
                                                         color=COLOR_ACCENT
                                                         ),
                                                 OptionButton(title="Ajustes del Motor y Reglas",
                                                              subtitle="Configuración profunda",
                                                              icon_image="icon_steampunk_sextant.png",
                                                              decor_image="texture_marble.png",
                                                              on_click=self.handle_click,
                                                              data="/ajustes"
                                                              ),
                                                 OptionButton(title="Crónica y Rendimiento ELO",
                                                              subtitle="Tus logros y rango",
                                                              icon_image="icon_steampunk_book.png",
                                                              decor_image="texture_marble.png",
                                                              on_click=self.handle_click,
                                                              data="/estadisticas"),
                                                 ]
                                       ),

                                   ]
                         )

    def handle_click(self, e: ft.ControlEvent) -> None:
        button_name = e.control.data

        # Definimos el SnackBar
        snack = ft.SnackBar(
            content=ft.Text(f"Iniciando: {button_name}", color=ft.Colors.BLACK),
            bgcolor=COLOR_ACCENT,
            duration=2500,
        )

        # Lo asignamos a la página y lo abrimos
        self.main_page.overlay.append(snack)  # Usar overlay es más robusto en versiones recientes
        snack.open = True
        self.main_page.update()

        self.main_page.go(button_name)