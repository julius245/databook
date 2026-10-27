# Controlador de autenticacion: inicio de sesion, registro y salir
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import _connect
from security import hash_password, check_password

auth_bp = Blueprint('auth', __name__)

# Maneja el inicio de sesion
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password(password, user['password']):
            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            session['role'] = user.get('rol', 'usuario')
            flash("Bienvenido al sistema", "success")
            return redirect(url_for('dashboard.index'))
        else:
            flash("Credenciales incorrectas", "danger")
            
    return render_template('web/login.html')

# Ruta para el registro de nuevos usuarios (Soluciona el error actual)
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        
        hashed_pw = hash_password(password)
        
        conn = _connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)",
                (nombre, email, hashed_pw, 'usuario')
            )
            conn.commit()
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            conn.rollback()
            flash("Error al registrar o el correo ya está registrado.", "danger")
        finally:
            conn.close()
            
    return render_template('web/register.html')

# Ruta para recuperar/cambiar contraseña
@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        flash("Funcionalidad de cambio de contraseña en desarrollo", "info")
        return redirect(url_for('auth.login'))
    
    return render_template('web/change_password.html')

# Cierra la sesion del usuario
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesion", "info")
    return redirect(url_for('web.index_web'))