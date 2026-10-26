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

# Cierra la sesion del usuario
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesion", "info")
    return redirect(url_for('web.index_web'))
