import re
import time
from playwright.sync_api import Page, expect


class HomePage:
    def __init__(self, page: Page):
        self.page = page

    def abrir(self, url: str = "http://localhost:8550") -> None:
        self.page.goto(url)

    def activar_accesibilidad(self) -> None:
        """Activa el árbol de semántica de Flet/Flutter de forma robusta."""
        print("DEBUG: Iniciando secuencia de activación de accesibilidad...")
        
        for i in range(5):  # Intentamos hasta 5 veces
            placeholder = self.page.locator("flt-semantics-placeholder")
            
            if placeholder.is_visible() or placeholder.inner_html() != "":
                placeholder.focus()
                self.page.keyboard.press("Enter")
            
            # Verificamos si la accesibilidad se activó buscando un texto conocido de la Home
            try:
                # "Opciones de Juego" es un texto estático en tu HomeView
                self.page.get_by_text("Opciones de Juego").wait_for(state="visible", timeout=3000)
                print(f"DEBUG: Accesibilidad confirmada en el intento {i+1}")
                return
            except Exception:
                print(f"DEBUG: Reintentando activación... ({i+1}/5)")
                self.page.wait_for_timeout(1000)
        
        print("WARNING: No se pudo confirmar la accesibilidad, procediendo de todos modos...")

    def verificar_titulo(self, texto_esperado: str) -> None:
        """Verifica el título de la pestaña del navegador."""
        expect(self.page).to_have_title(texto_esperado)

    def hacer_clic_en_boton(self, texto: str) -> None:
        """Busca un botón por su texto de accesibilidad (label o tooltip) y hace clic."""
        print(f"DEBUG: Buscando botón con texto: {texto}")
        
        # En Flet, cuando la accesibilidad está activa, los botones suelen tener
        # el rol 'button' y su nombre es el texto que contienen o su tooltip.
        boton = self.page.get_by_role("button", name=re.compile(texto, re.I))
        
        try:
            boton.wait_for(state="visible", timeout=10000)
            boton.scroll_into_view_if_needed()
            boton.click(timeout=5000)
            print(f"DEBUG: Clic realizado en '{texto}'")
        except Exception as e:
            print(f"DEBUG: Error al intentar clic por role: {e}")
            print("DEBUG: Intentando clic de emergencia buscando texto directamente...")
            # Fallback: buscar el texto y clickear lo que lo contiene
            target = self.page.get_by_text(texto, exact=False).first
            target.wait_for(state="visible", timeout=5000)
            target.click()

    def verificar_ruta(self, ruta_esperada: str) -> None:
        """Verifica que la URL termine en la ruta indicada."""
        regex = re.compile(f".*localhost:8550{ruta_esperada}$")
        expect(self.page).to_have_url(regex, timeout=5000)

    def verificar_encabezado(self, texto: str) -> None:
        """Verifica que un texto específico sea visible (si hay varios, acepta el primero)."""
        # Añadimos .first para evitar el strict mode violation si el texto aparece en AppBar y Body
        expect(self.page.get_by_text(texto, exact=True).first).to_be_visible(timeout=10000)
