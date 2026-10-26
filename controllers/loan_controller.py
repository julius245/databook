# Controlador para gestionar prestamos
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.database import _connect

loan_bp = Blueprint('loans', __name__, url_prefix='/prestamos')

# Muestra todos los prestamos
@loan_bp.route('/')
def list_loans():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prestamos ORDER BY fecha_prestamo DESC")
    prestamos = cursor.fetchall()
    conn.close()
    return render_template('aplicacion/prestamos.html', prestamos=prestamos)
