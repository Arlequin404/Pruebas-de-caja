# Importación de librerías necesarias para la aplicación web
from flask import Flask, render_template, request, redirect, session, url_for, flash, send_file
import psycopg2  # Para la conexión con la base de datos PostgreSQL
from datetime import datetime
import smtplib  # Para el envío de correos electrónicos
from email.mime.text import MIMEText
from pytz import timezone
import pytz  # Para trabajar con zonas horarias
import os
from dotenv import load_dotenv  # Para cargar variables de entorno desde un archivo .env
from email.utils import formataddr
import pandas as pd  # Para manipulación de datos y exportación a Excel
from io import BytesIO  # Para generar archivos en memoria

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Inicialización de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'secreto123'  # Clave secreta para manejo de sesiones

# Conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname='actas_db',
    user='postgres',
    password='8991',
    host='localhost'
)
cur = conn.cursor()

# Ruta de inicio: renderiza el formulario de login
@app.route('/')
def index():
    return render_template('login.html')

# Ruta para validar el inicio de sesión del usuario
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    cur.execute("SELECT id, nombre, rol FROM usuarios WHERE email=%s AND password=%s", (email, password))
    user = cur.fetchone()
    if user:
        # Almacena información del usuario en sesión si las credenciales son correctas
        session['user_id'] = user[0]
        session['nombre'] = user[1]
        session['rol'] = user[2]
        return redirect('/dashboard')
    flash("Correo o contraseña incorrecta", "danger")
    return redirect('/')

# Ruta para enviar un enlace de recuperación de contraseña al correo electrónico
@app.route('/enviar_recuperacion', methods=['POST'])
def enviar_recuperacion():
    email = request.form['email']

    # Verifica si el correo está registrado
    cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    user = cur.fetchone()

    if user:
        # Genera un token aleatorio como identificador de recuperación
        token = os.urandom(16).hex()
        reset_url = f"http://127.0.0.1:5000/restablecer_contraseña/{token}"

        # Crea el mensaje de correo con el enlace
        msg = MIMEText(f"""
        Hola,<br><br>
        Has solicitado cambiar tu contraseña. Haz clic en el siguiente enlace:<br>
        <a href=\"{reset_url}\">{reset_url}</a><br><br>
        Si no fuiste tú, ignora este mensaje.
        """, "html")

        msg["Subject"] = "Recuperación de contraseña"
        msg["From"] = formataddr(("Notificaciones", os.environ.get("SMTP_USER")))
        msg["To"] = email

        # Intenta enviar el correo
        try:
            with smtplib.SMTP("smtp.office365.com", 587) as server:
                server.starttls()
                server.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS"))
                server.send_message(msg)
            flash("Se ha enviado un enlace de recuperación al correo.", "success")
        except Exception as e:
            print("Error al enviar correo:", e)
            flash("Error al enviar el correo.", "danger")
    else:
        flash("Correo no registrado.", "warning")

    return redirect('/')

# Ruta del panel principal del usuario después del login
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('dashboard.html', nombre=session['nombre'])

# Ruta para creación de documentos (actas, informes o reportes)
@app.route('/crear/<tipo>', methods=['GET', 'POST'])
def crear(tipo):
    if 'user_id' not in session or session.get('rol') not in ['usuario', 'admin']:
        return 'Acceso no autorizado'


    if request.method == 'POST':
        asunto = request.form['asunto']
        observaciones = request.form['observaciones']
        tabla = tipo.lower()

        # Inserta el nuevo documento en la base de datos
        cur.execute(f"""
            INSERT INTO {tabla} (asunto, observaciones, id_usuario)
            VALUES (%s, %s, %s)
            RETURNING id, fecha, hora
        """, (asunto, observaciones, session['user_id']))
        new_id, fecha, hora = cur.fetchone()
        conn.commit()

        # Conversión de hora UTC a hora local Ecuador
        hora_utc = datetime.combine(fecha, hora).replace(tzinfo=pytz.utc)
        hora_local = hora_utc.astimezone(timezone('America/Guayaquil'))
        hora_formateada = hora_local.strftime("%H:%M:%S")

        # Enviar notificación por correo
        enviar_correo(session['nombre'], session['user_id'], new_id, tipo, fecha, hora_formateada, asunto, observaciones)

        # Mostrar notificación visual al usuario en pantalla
        from markupsafe import Markup
        flash(Markup(f"""
        <div class='toast-content'>
            <h5>Se ha registrado un nuevo <b>{tipo.lower()}</b> correctamente.</h5>
            <p><b>NÙMERO ASIGNADO:</b> {new_id}</p>
            <p><b>Asunto:</b> {asunto}</p>
            <p><b>Observaciones:</b> {observaciones}</p>
            <p><b>Fecha:</b> {fecha}</p>
            <p><b>Hora:</b> {hora_formateada}</p>
            <p><b>Funcionario:</b> {session['nombre']}</p>
        </div>
        """), 'toast')

        return redirect('/dashboard')
    return render_template('formulario.html', tipo=tipo)

# Función para simular envío de correo (puede ser real o de prueba)
def enviar_correo(nombre, user_id, doc_id, tipo, fecha, hora):
    cur.execute("SELECT email FROM usuarios WHERE id=%s", (user_id,))
    email = cur.fetchone()[0]
    print(f'[SIMULACIÓN] Email a {email} -> {tipo} ID {doc_id}, creado el {fecha} a las {hora} por {nombre}')

# Ruta para el panel de administración de usuarios
@app.route('/admin')
def admin():
    if session.get('rol') != 'admin':
        return 'Acceso denegado'
    cur.execute("SELECT id, nombre, email, rol FROM usuarios")
    usuarios = cur.fetchall()
    return render_template('admin.html', usuarios=usuarios)

# Ruta para ver todos los documentos (admin)
@app.route('/admin/documentos')
def admin_documentos():
    if session.get('rol') != 'admin':
        return 'Acceso denegado'

    # Consulta de todas las actas con datos del usuario que las registró
    cur.execute("""
        SELECT a.id, a.asunto, a.fecha, TO_CHAR(a.hora, 'HH24:MI:SS'), u.nombre
        FROM actas a JOIN usuarios u ON a.id_usuario = u.id
    """)
    actas = cur.fetchall()

    # Consulta de todos los informes
    cur.execute("""
        SELECT i.id, i.asunto, i.fecha, TO_CHAR(i.hora, 'HH24:MI:SS'), u.nombre
        FROM informes i JOIN usuarios u ON i.id_usuario = u.id
    """)
    informes = cur.fetchall()

    # Consulta de todos los reportes
    cur.execute("""
        SELECT r.id, r.asunto, r.fecha, TO_CHAR(r.hora, 'HH24:MI:SS'), u.nombre
        FROM reportes r JOIN usuarios u ON r.id_usuario = u.id
    """)
    reportes = cur.fetchall()

    return render_template('admin_documentos.html', actas=actas, informes=informes, reportes=reportes)


# Permite al administrador editar los campos "asunto" y "observaciones" de un documento (acta, informe o reporte) según su tipo e ID.
# Si se recibe un método POST, actualiza los valores en la base de datos.
# Si es GET, muestra el formulario con los datos actuales precargados.
@app.route('/editar/<tipo>/<int:id>', methods=['GET', 'POST'])
def editar_documento(tipo, id):
    if session.get('rol') != 'admin':
        return 'Acceso denegado'
    if request.method == 'POST':
        asunto = request.form['asunto']
        observaciones = request.form['observaciones']
        cur.execute(f"UPDATE {tipo} SET asunto=%s, observaciones=%s WHERE id=%s", (asunto, observaciones, id))
        conn.commit()
        flash(f'{tipo.capitalize()} ID {id} actualizado correctamente.', 'info')
        return redirect('/admin/documentos')
    cur.execute(f"SELECT asunto, observaciones FROM {tipo} WHERE id=%s", (id,))
    doc = cur.fetchone()
    return render_template('formulario.html', tipo=f"Editar {tipo}", asunto=doc[0], observaciones=doc[1])


# Permite al administrador eliminar un documento (acta, informe o reporte) por su tipo e ID.
# Solo accesible por usuarios con rol 'admin'.
@app.route('/eliminar/<tipo>/<int:id>')
def eliminar_documento(tipo, id):
    if session.get('rol') != 'admin':
        return 'Acceso denegado'
    cur.execute(f"DELETE FROM {tipo} WHERE id=%s", (id,))
    conn.commit()
    flash(f'{tipo.capitalize()} ID {id} eliminado correctamente.', 'danger')
    return redirect('/admin/documentos')


# Permite al administrador registrar un nuevo usuario en el sistema.
# Si se envía el formulario (POST), guarda el usuario con su rol y credenciales.
# Si se accede con GET, muestra el formulario de creación.
@app.route('/admin/usuarios/crear', methods=['GET', 'POST'])
def crear_usuario():
    if session.get('rol') != 'admin':
        return 'Acceso denegado'
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        rol = request.form['rol']
        cur.execute("INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)", 
                    (nombre, email, password, rol))
        conn.commit()
        flash("Usuario creado exitosamente", "success")
        return redirect('/admin')
    return render_template('form_usuario.html', modo="Crear", usuario=None)


# Permite al administrador editar los datos de un usuario específico por su ID.
# Actualiza nombre, email, contraseña y rol.
@app.route('/admin/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if session.get('rol') != 'admin':
        return 'Acceso denegado'
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        rol = request.form['rol']
        cur.execute("UPDATE usuarios SET nombre=%s, email=%s, password=%s, rol=%s WHERE id=%s",
                    (nombre, email, password, rol, id))
        conn.commit()
        flash("Usuario actualizado", "info")
        return redirect('/admin')
    cur.execute("SELECT nombre, email, password, rol FROM usuarios WHERE id=%s", (id,))
    usuario = cur.fetchone()
    return render_template('form_usuario.html', modo="Editar", usuario=usuario, id=id)


# Elimina completamente a un usuario del sistema según su ID.
# Accesible solo para administradores.
@app.route('/admin/usuarios/eliminar/<int:id>')
def eliminar_usuario(id):
    if session.get('rol') != 'admin':
        return 'Acceso denegado'
    cur.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    conn.commit()
    flash("Usuario eliminado", "danger")
    return redirect('/admin')



# Muestra al usuario logueado (rol usuario) todos los documentos registrados:
# actas, informes y reportes junto con observaciones, fechas y funcionario creador.
@app.route('/mis_documentos')
def mis_documentos():
    if session.get('rol') != 'usuario':
        return 'Acceso denegado'

    cur.execute("""
        SELECT a.id, a.asunto, a.observaciones, a.fecha, TO_CHAR(a.hora, 'HH24:MI:SS'), u.nombre
        FROM actas a JOIN usuarios u ON a.id_usuario = u.id
    """)
    actas = cur.fetchall()

    cur.execute("""
        SELECT i.id, i.asunto, i.observaciones, i.fecha, TO_CHAR(i.hora, 'HH24:MI:SS'), u.nombre
        FROM informes i JOIN usuarios u ON i.id_usuario = u.id
    """)
    informes = cur.fetchall()

    cur.execute("""
        SELECT r.id, r.asunto, r.observaciones, r.fecha, TO_CHAR(r.hora, 'HH24:MI:SS'), u.nombre
        FROM reportes r JOIN usuarios u ON r.id_usuario = u.id
    """)
    reportes = cur.fetchall()

    return render_template('mis_documentos.html', actas=actas, informes=informes, reportes=reportes)


# Envía un correo con los datos del documento creado al correo del funcionario que lo registró.
# Utiliza configuración SMTP leída desde el archivo .env.
def enviar_correo(nombre, user_id, doc_id, tipo, fecha, hora, asunto, observaciones):
    from dotenv import load_dotenv
    load_dotenv()

    cur.execute("SELECT email FROM usuarios WHERE id=%s", (user_id,))
    destinatario = cur.fetchone()[0]

    remitente_correo = os.environ.get("SMTP_USER")  # Ejemplo: notificaciones@controlelectrico.gob.ec
    remitente_nombre = "Notificaciones Control Eléctrico"
    password = os.environ.get("SMTP_PASS")

    msg = MIMEText(f"""
    <h3>Se ha registrado un nuevo <b>{tipo.lower()}</b> correctamente.</h3>
    <p><b>NÙMERO ASIGNADO:</b> {doc_id}</p>
    <p><b>Asunto:</b> {asunto}</p>
    <p><b>Observaciones:</b> {observaciones}</p>
    <p><b>Fecha:</b> {fecha}</p>
    <p><b>Hora:</b> {hora}</p>
    <p><b>Funcionario:</b> {nombre}</p>
    """, "html")

    msg["Subject"] = f"{tipo.capitalize()} creada: {asunto}"
    msg["From"] = formataddr((remitente_nombre, remitente_correo))
    msg["To"] = destinatario

    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(remitente_correo, password)
            server.send_message(msg)
            print("Correo enviado correctamente a", destinatario)
    except Exception as e:
        print("Error al enviar correo:", e)


# Permite restablecer la contraseña mediante un token único.
# Si se envía el formulario con nueva contraseña, actualiza el campo en la base de datos.
@app.route('/restablecer_contraseña/<token>', methods=['GET', 'POST'])
def restablecer_contraseña(token):
    if request.method == 'POST':
        nueva_contraseña = request.form['password']
        email = request.form['email']

        cur.execute("UPDATE usuarios SET password = %s WHERE email = %s", (nueva_contraseña, email))
        conn.commit()
        flash("Contraseña actualizada exitosamente.", "success")
        return redirect('/')

    return render_template('restablecer_contraseña.html', token=token)


# Muestra el formulario donde el usuario puede ingresar su email para solicitar recuperación de contraseña.
@app.route('/recuperar_contraseña', methods=['GET'])
def recuperar_contraseña():
    return render_template('recuperar_contraseña.html')


# Exporta a Excel todos los registros del tipo de documento especificado (actas, informes o reportes).
# Incluye campos: ID, Asunto, Observaciones, Fecha, Hora y Funcionario.
# Retorna un archivo descargable en formato .xlsx.
@app.route('/exportar_documentos/<tipo>')
def exportar_documentos(tipo):
    if tipo not in ['actas', 'informes', 'reportes']:
        return "Tipo no válido", 400

    # Consulta con observaciones
    cur.execute(f"""
        SELECT d.id, d.asunto, d.observaciones, d.fecha, TO_CHAR(d.hora, 'HH24:MI:SS'), u.nombre
        FROM {tipo} d JOIN usuarios u ON d.id_usuario = u.id
    """)
    datos = cur.fetchall()

    columnas = ["ID", "Asunto", "Observaciones", "Fecha", "Hora", "Funcionario"]
    df = pd.DataFrame(datos, columns=columnas)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=tipo.capitalize(), index=False)

    output.seek(0)
    filename = f"{tipo}_exportados.xlsx"
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def crear_usuario_directo(nombre, email, password, rol):
    conn = psycopg2.connect(
        dbname='actas_db',
        user='postgres',
        password='8991',
        host='localhost'
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)",
                (nombre, email, password, rol))
    conn.commit()
    cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cur.fetchone()
    conn.close()
    return usuario


# Cierra la sesión del usuario y redirige a la página de login.
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
