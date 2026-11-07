# Controlador de multas registradas por atraso
from flask import Blueprint, render_template, session, redirect, url_for
from models.database import _connect

fine_bp = Blueprint('fines', __name__, url_prefix='/multas')

@fine_bp.route('/')
def list_fines():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM multas ORDER BY fecha DESC")
    multas = cursor.fetchall()
    conn.close()
    return render_template('aplicacion/multas.html', multas=multas)
