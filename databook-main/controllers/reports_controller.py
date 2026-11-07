# Controlador para la generacion de reportes
from flask import Blueprint, render_template
from models.database import _connect

reports_bp = Blueprint('reports', __name__, url_prefix='/reportes')

@reports_bp.route('/')
def index():
    return render_template('aplicacion/reportes.html')
