import flet as ft
from views.styles import COLOR_ACCENT


@ft.control
class OptionButton(ft.Container):
    def __init__(self,
                 title: str,
                 subtitle: str,
                 icon_image: str,
                 decor_image: str,
                 on_click=None,
                 data=None
                 ) -> None:
        super().__init__(content=ft.Row(controls=[ft.Image(src=icon_image,
                                                           width=75,
                                                           height=75,
                                                           fit=ft.BoxFit.COVER
                                                           ),
                                                  ft.Column(controls=[ft.Text(title,
                                                                              size=16,
                                                                              weight=ft.FontWeight.BOLD,
                                                                              color=ft.Colors.BLACK),
                                                                      ft.Text(subtitle,
                                                                              size=12,
                                                                              color=ft.Colors.BLACK)
                                                                      ],
                                                            alignment=ft.MainAxisAlignment.CENTER,
                                                            )
                                                  ]
                                        )
                         )
        self.on_click = on_click
        self.data = data

        self.image = ft.DecorationImage(src=decor_image,
                                        fit=ft.BoxFit.COVER,
                                        opacity=0.8,  # Opcional: para que el fondo no sea tan fuerte
        )

        # --- EFECTOS VISUALES ---
        #self.bgcolor = ft.Colors.SURFACE  # Color base
        self.ink = True  # Efecto "Ripple" (ondas) al cliquear

        self.border_radius = 12
        #self.border = ft.Border.all(1, ft.Colors.with_opacity(0.3, COLOR_ACCENT))
        self.shadow = ft.BoxShadow(blur_radius=10,
                                   color=ft.Colors.with_opacity(0.5, COLOR_ACCENT)
                                   )



