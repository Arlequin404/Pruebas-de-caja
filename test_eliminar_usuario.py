from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

# Login
driver.get("http://localhost:5000/")
wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys("admin@correo.com")
driver.find_element(By.NAME, "password").send_keys("admin123")
driver.find_element(By.TAG_NAME, "form").submit()
time.sleep(2)

# Ir a la tabla de administración
driver.get("http://localhost:5000/admin")
time.sleep(2)

try:
    filas = driver.find_elements(By.XPATH, '//table/tbody/tr')
    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")
        if len(celdas) >= 3 and celdas[2].text.strip() == "selenium@correo.com":
            eliminar_btn = fila.find_element(By.XPATH, './/a[contains(text(), "Eliminar")]')
            eliminar_btn.click()
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            driver.switch_to.alert.accept()

            # Esperar a que la fila desaparezca
            WebDriverWait(driver, 10).until_not(
                lambda d: "selenium@correo.com" in d.page_source
            )

            print("✅ Usuario selenium@correo.com fue eliminado y confirmado.")
            break
    else:
        print("⚠️ No se encontró el usuario en ninguna fila.")
except Exception as e:
    print("❌ Error en la prueba:", e)

driver.quit()
