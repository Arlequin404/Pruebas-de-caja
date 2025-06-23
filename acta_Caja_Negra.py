from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

# Login como usuario
driver.get("http://localhost:5000/")
wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys("aaortis@uce.edu.ec")
driver.find_element(By.NAME, "password").send_keys("56789")
driver.find_element(By.TAG_NAME, "form").submit()
time.sleep(2)

# Crear acta
driver.get("http://localhost:5000/crear/actas")
wait.until(EC.presence_of_element_located((By.NAME, "asunto"))).send_keys("Acta prueba negra")
driver.find_element(By.NAME, "observaciones").send_keys("Observaciones desde caja negra")
driver.find_element(By.TAG_NAME, "form").submit()
time.sleep(2)

print("✅ Caja negra: acta creada desde la interfaz.")

driver.quit()
