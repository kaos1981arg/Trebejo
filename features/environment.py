from playwright.sync_api import sync_playwright
from behave.runner import Context
from behave.model import Scenario
import subprocess
from tests.pages.home_page import HomePage
import time
import os


def before_all(context: Context) -> None:
    # 1. Iniciamos el proceso de Flet en modo web (puerto 8550)
    # Esto evita el error de la pantalla gris al asegurar un entorno controlado
    context.flet_process = subprocess.Popen(
        ["python", "src/main.py"],
        env={
            **os.environ,
            "FLET_SERVER_PORT": "8550",
            "FLET_WEB_APP": "1",
            "FLET_FORCE_WEB_SERVER": "True",
        },
    )
    time.sleep(3)  # Esperamos a que el servidor levante

    # 2. Configuramos Playwright
    context.pw = sync_playwright().start()
    context.browser = context.pw.chromium.launch(
        headless=False
    )  # False para ver qué hace
    context.page = context.browser.new_page()


def after_all(context: Context) -> None:
    # Cerramos todo al finalizar
    context.browser.close()
    context.pw.stop()
    context.flet_process.terminate()


def before_scenario(context: Context, _scenario: Scenario) -> None:
    # Aquí ya tienes inicializado context.page (Playwright)
    # Instanciamos los Page Objects para que estén disponibles en todos los steps
    context.home_page = HomePage(context.page)
    # Si tienes más páginas, las agregas aquí:
    # context.duelo_page = DueloPage(context.page)
