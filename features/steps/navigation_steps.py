from behave import given, when, then, step
from behave.runner import Context


@given("que abro la aplicación Trebejo")
def open_app(context: Context) -> None:
    print("\nDEBUG: Abriendo aplicación...")
    context.home_page.abrir()


@step("activo el modo de accesibilidad")
def activate_accessibility(context: Context) -> None:
    print("DEBUG: Activando modo de accesibilidad...")
    context.home_page.activar_accesibilidad()
    print("DEBUG: Modo de accesibilidad activado.")


@then('el título de la página debería ser "{texto_esperado}"')
def check_title(context: Context, texto_esperado: str) -> None:
    context.home_page.verificar_titulo(texto_esperado)


@then('la ruta debería ser "{ruta_esperada}"')
@step('la ruta debería ser "{ruta_esperada}"')
def check_route(context: Context, ruta_esperada: str) -> None:
    context.home_page.verificar_ruta(ruta_esperada)


@when('hago clic en el botón con el texto "{texto_boton}"')
def click_button(context: Context, texto_boton: str) -> None:
    print(f"DEBUG: Intentando hacer clic en: {texto_boton}")
    context.home_page.hacer_clic_en_boton(texto_boton)


@then('debería ver el encabezado "{texto_encabezado}"')
def check_header(context: Context, texto_encabezado: str) -> None:
    context.home_page.verificar_encabezado(texto_encabezado)
