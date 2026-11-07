# Controlador para consultar el historial de actividad
from flask import Blueprint, render_template
from models.database import _connect

history_bp = Blueprint('history', __name__, url_prefix='/historial')

@history_bp.route('/')
def index():
    return render_template('aplicacion/historial.html')
