from playwright.sync_api import sync_playwright
import subprocess
import time
import os

def before_all(context):
    # 1. Iniciamos el proceso de Flet en modo web (puerto 8550)
    # Esto evita el error de la pantalla gris al asegurar un entorno controlado
    context.flet_process = subprocess.Popen(
        ["python", "src/main.py"],
        env={**os.environ,
             "FLET_SERVER_PORT": "8550",
             "FLET_WEB_APP": "1",
             "FLET_FORCE_WEB_SERVER":"True"
             }
    )
    time.sleep(3)  # Esperamos a que el servidor levante

    # 2. Configuramos Playwright
    context.pw = sync_playwright().start()
    context.browser = context.pw.chromium.launch(headless=False) # False para ver qué hace
    context.page = context.browser.new_page()

def after_all(context):
    # Cerramos todo al finalizar
    context.browser.close()
    context.pw.stop()
    context.flet_process.terminate()