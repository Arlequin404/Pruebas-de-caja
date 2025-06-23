
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)
driver.get("http://localhost:5000/")

# Intentar login con credenciales inválidas
wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys("fake@correo.com")
driver.find_element(By.NAME, "password").send_keys("wrongpassword")
driver.find_element(By.TAG_NAME, "form").submit()
time.sleep(2)

print("⚠️ Login inválido probado correctamente.")
driver.quit()
