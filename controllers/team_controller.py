# Controlador de "Mi Equipo": bibliotecarios/staff que el usuario agrega a su cuenta
import secrets

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models.database import _connect
from controllers.geo_data import get_document_types
from security import hash_password

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


def _acceso_equipo():
    """Devuelve una redirección si no hay sesión o si el rol no puede administrar el equipo."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('rol') not in ('staff', 'superadmin'):
        return redirect(url_for('dashboard.index'))
    return None


@team_bp.route('/')
def index():
    denegado = _acceso_equipo()
    if denegado:
        return denegado

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


# Crea un bibliotecario nuevo con una contraseña temporal que se muestra una sola vez
@team_bp.route('/nuevo', methods=['POST'])
def new_librarian():
    denegado = _acceso_equipo()
    if denegado:
        return denegado

    f = request.form
    dato = lambda campo: f.get(campo, '').strip()
    primer_nombre, primer_apellido = dato('primer_nombre'), dato('primer_apellido')
    tipo_documento, numero_documento = dato('tipo_documento'), dato('numero_documento')
    email, telefono = dato('email').lower(), dato('telefono')

    rol_equipo = dato('rol_equipo')
    if rol_equipo not in ROLES:
        rol_equipo = 'otro'
    if rol_equipo == 'otro':
        rol_equipo = dato('rol_equipo_otro')      # texto libre; la plantilla lo muestra tal cual

    error = None
    if not (primer_nombre and primer_apellido and email):
        error = 'Completa el nombre, el apellido y el correo.'
    elif '@' not in email:
        error = 'El correo no es válido.'
    elif tipo_documento not in get_document_types():
        error = 'Selecciona un tipo de documento válido.'
    elif not (numero_documento.isdigit() and 8 <= len(numero_documento) <= 10):
        error = 'El número de identificación debe tener entre 8 y 10 dígitos.'
    elif telefono and not (telefono.isdigit() and 7 <= len(telefono) <= 10):
        error = 'El teléfono debe tener entre 7 y 10 dígitos.'
    elif not rol_equipo:
        error = 'Especifica el rol del nuevo miembro.'
    if error:
        flash(error, 'danger')
        return redirect(url_for('team.index'))

    # Nivel por módulo; cualquier valor desconocido queda como "sin acceso"
    permisos = {m: (dato('permiso_' + m) if dato('permiso_' + m) in LEVELS else 'sin_acceso') for m in MODULES}
    modulos = ','.join(m for m, nivel in permisos.items() if nivel != 'sin_acceso')

    nombre = ' '.join(x for x in (primer_nombre, dato('segundo_nombre'), primer_apellido, dato('segundo_apellido')) if x)
    temporal = secrets.token_urlsafe(9)

    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute("""INSERT INTO usuarios
                         (nombre, email, password_hash, rol, creado_por, estado, modulos_permitidos,
                          password_temporal, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
                          tipo_documento, numero_documento, telefono, rol_equipo,
                          permiso_catalogo, permiso_miembros, permiso_prestamos, permiso_multas)
                       VALUES (%s, %s, %s, 'bibliotecario', %s, 'Activo', %s,
                               1, %s, %s, %s, %s,
                               %s, %s, %s, %s,
                               %s, %s, %s, %s)""",
                    (nombre, email, hash_password(temporal), session['user_id'], modulos,
                     primer_nombre, dato('segundo_nombre') or None, primer_apellido, dato('segundo_apellido') or None,
                     tipo_documento, numero_documento, telefono or None, rol_equipo,
                     permisos['catalogo'], permisos['miembros'], permisos['prestamos'], permisos['multas']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        if getattr(e, 'pgcode', None) == '23505':          # correo repetido (UNIQUE)
            flash('Ya existe una cuenta con ese correo.', 'danger')
        else:
            print(f"Error creando miembro del equipo: {e}")
            flash('No se pudo crear el miembro. Intenta de nuevo.', 'danger')
        return redirect(url_for('team.index'))
    finally:
        conn.close()

    flash(f'Miembro creado. Contraseña temporal: {temporal} — cópiala ahora, no se volverá a mostrar.', 'success')
    return redirect(url_for('team.index'))
