# Controlador para la administracion de miembros y usuarios
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.database import _connect

member_bp = Blueprint('members', __name__, url_prefix='/miembros')

@member_bp.route('/')
def list_members():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios ORDER BY id DESC")
    miembros = cursor.fetchall()
    conn.close()
    return render_template('aplicacion/cuentas.html', miembros=miembros)
