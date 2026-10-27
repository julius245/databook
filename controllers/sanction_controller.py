# Controlador de sanciones a usuarios
from flask import Blueprint, render_template
from models.database import _connect

sanction_controller = Blueprint('sanctions', __name__, url_prefix='/sanciones')

@sanction_controller.route('/')
def index():
    return render_template('aplicacion/sanciones.html')
