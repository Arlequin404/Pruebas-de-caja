from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import psycopg2
import time

# Conexión a la base de datos
conn = psycopg2.connect(
    dbname='actas_db',
    user='postgres',
    password='8991',
    host='localhost'
)
cur = conn.cursor()

# Datos de prueba
correo_prueba = "gris@correo.com"
nombre = "Prueba Gris"
password = "gris123"
rol = "usuario"

# Selenium (interfaz)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

# Login como admin
driver.get("http://localhost:5000/")
wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys("admin@correo.com")
driver.find_element(By.NAME, "password").send_keys("admin123")
driver.find_element(By.TAG_NAME, "form").submit()
time.sleep(2)

# Ir a crear usuario
driver.get("http://localhost:5000/admin/usuarios/crear")
wait.until(EC.presence_of_element_located((By.NAME, "nombre"))).send_keys(nombre)
driver.find_element(By.NAME, "email").send_keys(correo_prueba)
driver.find_element(By.NAME, "password").send_keys(password)
driver.find_element(By.NAME, "rol").send_keys(rol)
driver.find_element(By.TAG_NAME, "form").submit()

# Esperar a que redireccione al panel de admin
WebDriverWait(driver, 10).until(EC.url_contains("/admin"))
time.sleep(1)

# Verificación con reintento
usuario = None
for _ in range(5):
    cur.execute("SELECT * FROM usuarios WHERE email=%s", (correo_prueba,))
    usuario = cur.fetchone()
    if usuario:
        break
    time.sleep(1)

if usuario:
    print("✅ Prueba de caja gris exitosa. Usuario creado correctamente:")
    print("ID:", usuario[0], "| Nombre:", usuario[1], "| Email:", usuario[2], "| Rol:", usuario[4])
else:
    print("❌ Fallo en la prueba de caja gris: el usuario no fue encontrado en la base de datos.")

# Limpieza (eliminar usuario creado)
cur.execute("DELETE FROM usuarios WHERE email=%s", (correo_prueba,))
conn.commit()

# Cerrar todo
driver.quit()
cur.close()
conn.close()
