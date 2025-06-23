from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import psycopg2
import time

asunto = "Acta gris con verificación"
observaciones = "Hecha desde caja gris"
correo_usuario = "aaortis@uce.edu.ec"

conn = psycopg2.connect(
    dbname='actas_db',
    user='postgres',
    password='8991',
    host='localhost'
)
cur = conn.cursor()

# Selenium
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

# Login
driver.get("http://localhost:5000/")
wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(correo_usuario)
driver.find_element(By.NAME, "password").send_keys("56789")
driver.find_element(By.TAG_NAME, "form").submit()
time.sleep(2)

# Crear acta
driver.get("http://localhost:5000/crear/actas")
wait.until(EC.presence_of_element_located((By.NAME, "asunto"))).send_keys(asunto)
driver.find_element(By.NAME, "observaciones").send_keys(observaciones)
driver.find_element(By.TAG_NAME, "form").submit()
time.sleep(2)
driver.quit()

# Verificar en base de datos
cur.execute("SELECT id, asunto FROM actas ORDER BY id DESC LIMIT 1")
fila = cur.fetchone()

if fila and fila[1] == asunto:
    print("✅ Caja gris: acta creada y verificada en la base de datos. ID:", fila[0])
    cur.execute("DELETE FROM actas WHERE id = %s", (fila[0],))
    conn.commit()
else:
    print("❌ Caja gris: no se encontró el acta en la base de datos.")

cur.close()
conn.close()
