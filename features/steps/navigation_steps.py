from behave import given, when, then
from behave.runner import Context
from playwright.sync_api import expect


@given("que abro la aplicación Trebejo")
def open_app(context: Context) -> None:
    context.home_page.abrir()


@given("activo el modo de accesibilidad")
def activate_accessibility(context: Context) -> None:
    context.home_page.activar_accesibilidad()


@then('el título de la página debería ser "{texto_esperado}"')
def check_title(context: Context, texto_esperado: str) -> None:
    context.home_page.verificar_titulo(texto_esperado)


@then('la ruta debería ser "{ruta_esperada}"')
def check_route(context: Context, ruta_esperada: str) -> None:
    context.home_page.verificar_ruta(ruta_esperada)


@when('hago clic en el botón con el texto "{texto_boton}"')
def click_button(context: Context, texto_boton: str) -> None:
    context.home_page.hacer_clic_en_boton(texto_boton)
