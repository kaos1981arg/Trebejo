import re
from playwright.sync_api import Page, expect


class HomePage:
    def __init__(self, page: Page):
        self.page = page
        # Podemos definir locatarios fijos aquí si quisiéramos
        # self.logo = page.get_by_role("img", name="Logo")

    def abrir(self, url: str = "http://localhost:8550") -> None:
        self.page.goto(url)

    def activar_accesibilidad(self) -> None:
        """Activa el árbol de semántica de Flet/Flutter."""
        placeholder = self.page.locator("flt-semantics-placeholder")
        placeholder.wait_for(state="attached")
        placeholder.focus()
        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(2000)

    def verificar_titulo(self, texto_esperado: str) -> None:
        """Verifica el título de la pestaña del navegador."""
        expect(self.page).to_have_title(texto_esperado)

    def hacer_clic_en_boton(self, texto: str) -> None:
        """Busca un botón por texto usando regex y hace clic."""
        # Centralizamos la lógica de Flet (role + regex) aquí
        boton = self.page.get_by_role("button", name=re.compile(texto, re.I))
        boton.scroll_into_view_if_needed()
        boton.click(timeout=5000)

    def verificar_ruta(self, ruta_esperada: str) -> None:
        """Verifica que la URL termine en la ruta indicada."""
        regex = re.compile(f".*localhost:8550{ruta_esperada}$")
        expect(self.page).to_have_url(regex, timeout=5000)
