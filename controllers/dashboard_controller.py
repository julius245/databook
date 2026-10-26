# Controlador del dashboard del usuario
from flask import Blueprint, render_template, session, redirect, url_for
from models.database import _connect

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Carga la vista principal con indicadores rapidos
@dashboard_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM libros")
    total_libros = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM prestamos WHERE estado = 'activo'")
    total_prestamos = cursor.fetchone()['total']
    conn.close()
    
    return render_template('aplicacion/dashboard.html', total_libros=total_libros, total_prestamos=total_prestamos)
