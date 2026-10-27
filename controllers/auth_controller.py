# Controlador de autenticacion: inicio de sesion, registro y salir
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import psycopg2.extras
from models.database import _connect
from security import hash_password, check_password
from controllers.geo_data import get_countries, get_timezones, get_document_types

auth_bp = Blueprint('auth', __name__)

# Maneja el inicio de sesion
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = _connect()
        # Usamos RealDictCursor para que los resultados sean diccionarios con nombres de columnas
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            session['role'] = user.get('rol', 'usuario')
            # Claves que utilizan las plantillas de la aplicación
            session['usuario_nombre'] = user['nombre']
            session['rol'] = user.get('rol', 'usuario')
            session['modulos'] = (user.get('modulos_permitidos') or '').split(',')
            flash("Bienvenido al sistema", "success")
            return redirect(url_for('dashboard.index'))
        else:
            flash("Credenciales incorrectas", "danger")
            
    return render_template('web/login.html')

# Ruta para el registro de nuevos usuarios
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Capturamos los campos enviados por el formulario wizard
        primer_nombre = request.form.get('primer_nombre', '').strip()
        primer_apellido = request.form.get('primer_apellido', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Unimos nombre y apellido si tu tabla de base de datos solo tiene la columna 'nombre'
        nombre_completo = f"{primer_nombre} {primer_apellido}"
        
        hashed_pw = hash_password(password)
        
        conn = _connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuarios (nombre, email, password_hash, rol, primer_nombre, primer_apellido) VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre_completo, email, hashed_pw, 'usuario', primer_nombre, primer_apellido)
            )
            conn.commit()
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            conn.rollback()
            print(f"Error en registro: {e}") # Para que lo veas en la terminal
            flash("Error al registrar: el correo ya está registrado o faltan datos.", "danger")
            # Devolvemos los datos al formulario para que el usuario no tenga que rescribir todo
            return render_template('web/register.html', data=request.form)
        finally:
            conn.close()
            
    return render_template(
        'web/register.html',
        countries=get_countries(),
        timezones=get_timezones(),
        document_types=get_document_types()
    )

# Ruta para recuperar/cambiar contraseña
@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        flash("Funcionalidad de cambio de contraseña en desarrollo", "info")
        return redirect(url_for('auth.login'))
    
    return render_template('web/cambiar_password.html')

# Ruta para autenticación de Google (Soluciona el error actual)
@auth_bp.route('/google-auth', methods=['POST'])
def google_auth():
    return {"status": "success", "message": "Google auth en desarrollo"}, 200

# Perfil del usuario autenticado
@auth_bp.route('/perfil')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))

        full_name = user.get('nombre') or 'Usuario'
        permissions = {
            'catalogo': user.get('permiso_catalogo', 'control_total'),
            'miembros': user.get('permiso_miembros', 'control_total'),
            'prestamos': user.get('permiso_prestamos', 'control_total'),
            'multas': user.get('permiso_multas', 'control_total'),
        }
        library = session.get('biblioteca_nombre')
        return render_template(
            'aplicacion/perfil.html',
            user=user,
            full_name=full_name,
            library=library,
            staff_email=None,
            permissions=permissions,
        )
    finally:
        conn.close()


# Ajustes del usuario autenticado
@auth_bp.route('/ajustes')
def settings():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))

        library_config = None
        try:
            cursor.execute("SELECT * FROM configuracion_biblioteca WHERE id = 1")
            library_config = cursor.fetchone()
        except Exception:
            library_config = None

        return render_template(
            'aplicacion/ajustes.html',
            user=user,
            library=library_config.get('nombre') if library_config else session.get('biblioteca_nombre'),
            library_config=library_config,
            current_theme=user.get('tema', 'sistema'),
            document_types=get_document_types(),
        )
    finally:
        conn.close()


# Cierra la sesion del usuario autenticado
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesion", "info")
    return redirect(url_for('index'))