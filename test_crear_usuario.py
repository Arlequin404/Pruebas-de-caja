from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Iniciar navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

# Paso 1: Ir al login (en tu caso es la raíz /)
driver.get("http://localhost:5000/")

# Paso 2: Iniciar sesión como admin
wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys("admin@correo.com")
driver.find_element(By.NAME, "password").send_keys("admin123")
driver.find_element(By.TAG_NAME, "form").submit()

# Esperar redirección
time.sleep(2)

# Paso 3: Ir al formulario de creación de usuario
driver.get("http://localhost:5000/admin/usuarios/crear")

# Paso 4: Llenar formulario de nuevo usuario
wait.until(EC.presence_of_element_located((By.NAME, "nombre"))).send_keys("Usuario Selenium")
driver.find_element(By.NAME, "email").send_keys("selenium@correo.com")
driver.find_element(By.NAME, "password").send_keys("clave123")
driver.find_element(By.NAME, "rol").send_keys("usuario")
driver.find_element(By.TAG_NAME, "form").submit()

# Esperar para ver el resultado
time.sleep(3)
print("✅ Prueba completada con login y creación de usuario.")

# Cerrar navegador
driver.quit()
