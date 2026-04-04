import flet as ft
from views.home_view import HomeView

ASSETS_PATH = "../assets"

def main(page: ft.Page) -> None:
    page.title = "Trebejo"
    page.window.always_on_top = True
    page.scroll = ft.ScrollMode.ADAPTIVE
    # En PC, esto limita el ancho para que no se vea "estirada"
    page.window.width = 450
    page.window.height = 650
    # Alineación central para que en pantallas grandes se vea prolijo
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    # Para que los elementos ocupen el ancho disponible (hasta el límite de 450)
    page.padding = 20

    # 1. Diccionario de rutas (Mapeo)
    router = {
        "/": HomeView,
    }

    # 2. Función manejadora de cambios de ruta
    def route_change(_: ft.RouteChangeEvent | None) -> None:
        page.views.clear()
        print("Route change")

        # Obtenemos la clase según la ruta actual
        view_class = router.get(page.route)

        if view_class:
            page.views.append(view_class(page))
        else:
            page.views.append(ft.View(route="/404", controls=[ft.Text("404 - No encontrado")]))

        page.update()

    # 3. Configuración de eventos
    page.on_route_change = route_change
    #page.on_view_pop = lambda _: page.views.pop() and page.update()
    #page.on_view_pop = view_pop

    # 4. Navegar a la ruta inicial
    page.route = "/"
    route_change(None)

if __name__ == "__main__":

    ft.run(main=main,
           view=ft.AppView.FLET_APP_WEB,
           assets_dir=ASSETS_PATH,
           )
