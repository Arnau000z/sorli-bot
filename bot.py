import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
print(">>> VERSION ACTUAL DEL BOT LOADED")


URL = "https://www.sorlisport.com/ca/fitness/reserva"

# =============================
#  DIAS → CLASES A RESERVAR
# =============================
CLASES = {
    "sabado": [("PILATES", "10:15"), ("ESTIRAMENTS", None)],
    "domingo": [("POSTURAL", "11:15")],
    "miercoles": [("PILATES", "10:15")],
    "jueves": [("ESPALDA SANA", "11:15")],
    "viernes": [("PILATES", "10:15")]
}

def obtener_clases_a_reservar():
    hoy = datetime.datetime.now().strftime("%A").lower()

    traducciones = {
        "saturday": "sabado",
        "sunday": "domingo",
        "monday": "lunes",
        "tuesday": "martes",
        "wednesday": "miercoles",
        "thursday": "jueves",
        "friday": "viernes"
    }

    return CLASES.get(traducciones[hoy], [])


from selenium.webdriver.chrome.service import Service

def crear_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # Usar Service + ChromeDriverManager (versión compatible con Selenium nuevo)
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(
        service=service,
        options=options
    )
    return driver



def login(driver):
    driver.get(URL)
    time.sleep(3)

    # Clic en "Iniciar sessió"
    driver.find_element(By.LINK_TEXT, "Iniciar sessió").click()
    time.sleep(2)

    # Rellenar usuario y contraseña
    email = driver.find_element(By.ID, "email")
    pwd = driver.find_element(By.ID, "password")

    email.send_keys(os.getenv("SORLI_USER"))
    pwd.send_keys(os.getenv("SORLI_PASS"))

    pwd.submit()
    time.sleep(4)


def reservar_clase(driver, nombre, hora):
    print(f"🔎 Buscando clase: {nombre} {hora if hora else ''}")

    # Buscar por NOMBRE en un <b>
    actividades = driver.find_elements(By.XPATH, f"//b[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{nombre.upper()}')]")

    if not actividades:
        print("❌ Clase no encontrada.")
        return False

    for actividad in actividades:
        try:
            # Buscar el botón RESERVA dentro del mismo bloque de actividad
            reserva_bold = actividad.find_element(
                By.XPATH,
                ".//ancestor::div[contains(@class,'actividad')]//b[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'RESERVA')]"
            )

            # Botón real está justo antes
            boton = reserva_bold.find_element(By.XPATH, "./preceding::button[1]")
            boton.click()
            time.sleep(2)

            # Confirmar reserva
            confirmar = driver.find_element(By.XPATH, "//button[contains(text(),'CONFIRMAR RESERVA')]")
            confirmar.click()

            print("✅ ¡Clase reservada!")
            return True

        except Exception as e:
            print("⚠ No se pudo reservar esta instancia:", e)

    return False


def main():
    clases_hoy = obtener_clases_a_reservar()
    if not clases_hoy:
        print("Hoy no toca reservar nada.")
        return

    driver = crear_driver()

    try:
        login(driver)
        time.sleep(1)

        for nombre, hora in clases_hoy:
            reservar_clase(driver, nombre, hora)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
