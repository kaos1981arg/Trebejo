from behave import given, when, then
from behave.runner import Context
from playwright.sync_api import expect
import re

@given('que abro la aplicación Trebejo')
def open_app(context: Context) -> None  :
    context.page.goto("http://localhost:8550")

@given('activo el modo de accesibilidad')
def activate_accessibility(context: Context)-> None:
    placeholder = context.page.locator("flt-semantics-placeholder")
    placeholder.wait_for(state="attached")
    placeholder.focus()
    context.page.keyboard.press("Enter")  # Esto activa la semántica sin importar la posición
    context.page.wait_for_timeout(2000)

@then('el título de la página debería ser "{texto_esperado}"')
def check_title(context: Context, texto_esperado: str)-> None:
    # Verificamos que el encabezado o texto aparezca en la nueva vista
    expect(context.page).to_have_title(texto_esperado)

@then('la ruta debería ser "{ruta_esperada}"')
def check_route(context: Context, ruta_esperada: str)-> None:
    # Usamos una expresión regular para verificar que la URL termina en la ruta
    # Esto ignora si es http://localhost:8550 o http://127.0.0.1:8550
    regex = re.compile(f".*localhost:8550{ruta_esperada}$")

    # expect reintenta automáticamente si la app está redirigiendo
    expect(context.page).to_have_url(regex)

@when('hago clic en el botón con el texto "{texto_boton}"')
def click_button(context: Context, texto_boton: str)-> None:
    context.page.get_by_role("button", name=re.compile(texto_boton)).click(timeout=3000)