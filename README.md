# Sistema de Registro de Actas - Pruebas de Software

Este proyecto es un sistema web para la gestión de actas, desarrollado en Flask, con pruebas automatizadas que aplican técnicas de **caja negra**, **caja blanca** y **caja gris**.

## 📁 Estructura del Proyecto

```
actas_app/
├── app.py                   # Aplicación principal Flask
├── config.py                # Configuración del sistema
├── templates/               # Archivos HTML
├── static/                  # Archivos CSS/JS
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias
├── tests y scripts de prueba:
│   ├── acta_Caja_Negra.py
│   ├── acta_caja_blanca.py
│   ├── acta_caja_gris.py
│   ├── test_funcion_crear_usuario.py
│   ├── test_crear_usuario.py
│   ├── test_eliminar_usuario.py
│   ├── test_caja_gris.py
│   └── test_login_invalido.py
```

## 🧪 Tipos de pruebas incluidas

### 🔲 Caja Negra
- `acta_Caja_Negra.py`: Usa Selenium para crear un acta desde la interfaz como usuario.
- `test_login_invalido.py`: Prueba que un login incorrecto sea rechazado.

### ⚪ Caja Blanca
- `acta_caja_blanca.py`: Realiza POST directo al backend para crear un acta, verificando la lógica interna.
- `test_funcion_crear_usuario.py`: Prueba lógica interna de creación de usuario.

### ⚫ Caja Gris
- `acta_caja_gris.py` y `test_caja_gris.py`: Usan Selenium para operar en la interfaz, y luego acceden a la base de datos PostgreSQL para verificar los registros.

## ▶️ Ejecución de pruebas

Asegúrate de tener PostgreSQL, Python 3 y Google Chrome instalados. Luego ejecuta:

```bash
# Crear entorno virtual (opcional)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pruebas
python3 acta_Caja_Negra.py
python3 test_funcion_crear_usuario.py
python3 acta_caja_blanca.py
python3 test_caja_gris.py
python3 acta_caja_gris.py
python3 test_login_invalido.py
```

## 💾 Base de Datos

Asegúrate de tener PostgreSQL corriendo y crea una base de datos llamada `actas_db`. Las credenciales están configuradas en `.env`.

## 📦 Tecnologías usadas

- Python + Flask
- Selenium (para pruebas de interfaz)
- psycopg2 (para conexión a PostgreSQL)
- unittest (para pruebas internas)
- HTML + CSS (para frontend básico)

## 👨‍💻 Autor

Este proyecto fue elaborado como parte del estudio de técnicas de pruebas de software.
