# Controlador exclusivo para el rol de superadministrador
from flask import Blueprint, render_template, session, redirect, url_for
from models.database import _connect

superadmin_bp = Blueprint('superadmin', __name__, url_prefix='/superadmin')

@superadmin_bp.route('/')
def index():
    if session.get('role') != 'superadmin':
        return redirect(url_for('dashboard.index'))
    return render_template('aplicacion/superadmin.html')
