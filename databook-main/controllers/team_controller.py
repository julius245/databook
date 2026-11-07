# Controlador para la vista del equipo de desarrollo
from flask import Blueprint, render_template

team_bp = Blueprint('team', __name__, url_prefix='/equipo')

@team_bp.route('/')
def index():
    return render_template('aplicacion/equipo.html')
