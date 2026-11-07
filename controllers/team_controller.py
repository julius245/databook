# Controlador de "Mi Equipo": bibliotecarios/staff que el usuario agrega a su cuenta
from flask import Blueprint, render_template, request, session, redirect, url_for
from models.database import _connect
from controllers.geo_data import get_document_types

team_bp = Blueprint('team', __name__, url_prefix='/equipo')

# Módulos del sistema y niveles de permiso (los mismos que usa has_permission en las plantillas)
MODULES = {
    'catalogo': 'Catálogo',
    'miembros': 'Miembros',
    'prestamos': 'Préstamos',
    'multas': 'Multas',
}
LEVELS = {
    'sin_acceso': 'Sin acceso',
    'lectura': 'Solo lectura',
    'editor': 'Editor',
    'control_total': 'Control total',
}


def _permisos(catalogo, miembros, prestamos, multas):
    return {'catalogo': catalogo, 'miembros': miembros, 'prestamos': prestamos, 'multas': multas}


# Roles predefinidos: al elegir uno, el formulario autocompleta los permisos por módulo
ROLES = {
    'bibliotecario_completo': {
        'etiqueta': 'Bibliotecario (acceso completo)',
        'permisos': _permisos('control_total', 'control_total', 'control_total', 'control_total'),
    },
    'auxiliar_prestamos': {
        'etiqueta': 'Auxiliar de préstamos',
        'permisos': _permisos('lectura', 'editor', 'control_total', 'editor'),
    },
    'catalogador': {
        'etiqueta': 'Catalogador',
        'permisos': _permisos('control_total', 'lectura', 'lectura', 'sin_acceso'),
    },
    'consulta': {
        'etiqueta': 'Solo consulta',
        'permisos': _permisos('lectura', 'lectura', 'lectura', 'lectura'),
    },
    'otro': {'etiqueta': 'Otro', 'permisos': {}},
}


@team_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    role_filter = request.args.get('rol', '').strip()
    if role_filter not in ROLES:
        role_filter = ''

    sql = "SELECT * FROM usuarios WHERE creado_por = %s"
    params = [session['user_id']]
    if role_filter:
        sql += " AND rol_equipo = %s"
        params.append(role_filter)
    sql += " ORDER BY nombre"

    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        librarians = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        'aplicacion/equipo.html',
        librarians=librarians,
        roles=ROLES,
        modules=MODULES,
        levels=LEVELS,
        document_types=get_document_types(),
        role_filter=role_filter,
    )
