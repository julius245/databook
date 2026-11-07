# Controlador para la generacion de reportes
from datetime import date

from flask import Blueprint, render_template, request, session, redirect, url_for
from models.database import _connect
from controllers.dashboard_controller import _hoy, _primer_dia_mes

reports_bp = Blueprint('reports', __name__, url_prefix='/reportes')

PERIODOS = {'mes': 'este mes', 'trimestre': 'últimos 3 meses', 'anio': 'este año'}
MENORES = 'TARJETA DE IDENTIDAD'          # valor de miembros.tipo que identifica a los menores
NOMBRE_MIEMBRO = "(m.primer_nombre || ' ' || m.primer_apellido)"
FECHA_OK = r"^\d{4}-\d{2}-\d{2}"          # evita errores al convertir fechas mal escritas


def _porcentajes(filas, etiqueta):
    """Convierte [{'nombre': x, 'n': 3}, ...] en [{etiqueta: x, 'valor': % del total}, ...]."""
    total = sum(f['n'] for f in filas)
    return [{etiqueta: f['nombre'], 'valor': round(f['n'] * 100 / total)} for f in filas] if total else []


@reports_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    period = request.args.get('periodo', 'mes')
    if period not in PERIODOS:
        period = 'mes'

    conn = _connect()
    try:
        cur = conn.cursor()
        hoy = _hoy(cur)
        inicio = {'mes': _primer_dia_mes(hoy, 0),
                  'trimestre': _primer_dia_mes(hoy, 2),
                  'anio': date(hoy.year, 1, 1)}[period].isoformat()

        # --- Catálogo ---
        cur.execute("""SELECT COUNT(*) AS titulos,
                              COALESCE(SUM(total_ejemplares), 0) AS copias,
                              COALESCE(SUM(disponibles), 0) AS disp FROM libros""")
        r = cur.fetchone()
        titulos, copias, disponibles = r['titulos'], int(r['copias']), int(r['disp'])

        # --- Miembros ---
        cur.execute("""SELECT COUNT(*) AS total,
                              COUNT(*) FILTER (WHERE estado = 'Activo') AS activos,
                              COUNT(*) FILTER (WHERE UPPER(tipo) = %s) AS menores
                       FROM miembros""", (MENORES,))
        r = cur.fetchone()
        miembros, miembros_activos, menores = r['total'], r['activos'], r['menores']

        cur.execute("SELECT tipo AS nombre, COUNT(*) AS n FROM miembros GROUP BY tipo ORDER BY n DESC")
        tipo_documento = _porcentajes(cur.fetchall(), 'nombre')

        # --- Préstamos del período ---
        cur.execute("""SELECT COUNT(*) AS total,
                         COUNT(*) FILTER (WHERE estado = 'Devuelto' AND fecha_devuelto IS NOT NULL
                              AND LEFT(fecha_devuelto, 10) <= LEFT(fecha_devolucion, 10)) AS tiempo,
                         COUNT(*) FILTER (WHERE estado = 'Devuelto' AND fecha_devuelto IS NOT NULL
                              AND LEFT(fecha_devuelto, 10) > LEFT(fecha_devolucion, 10)) AS retrasadas
                       FROM prestamos WHERE LEFT(fecha_prestamo, 10) >= %s""", (inicio,))
        prestamos = cur.fetchone()

        # CASE evita convertir fechas mal escritas (Postgres no garantiza el orden de los filtros)
        cur.execute("""SELECT l.categoria AS categoria,
                              COALESCE(ROUND(AVG(CASE WHEN p.fecha_devuelto ~ %s AND p.fecha_prestamo ~ %s
                                  THEN LEFT(p.fecha_devuelto, 10)::date - LEFT(p.fecha_prestamo, 10)::date END)), 0)::int AS dias
                       FROM prestamos p JOIN libros l ON l.id = p.libro_id
                       WHERE p.fecha_devuelto IS NOT NULL AND LEFT(p.fecha_prestamo, 10) >= %s
                       GROUP BY l.categoria ORDER BY dias DESC LIMIT 5""", (FECHA_OK, FECHA_OK, inicio))
        duracion = cur.fetchall()

        cur.execute("""SELECT l.titulo, COUNT(*) AS prestamos
                       FROM prestamos p JOIN libros l ON l.id = p.libro_id
                       WHERE LEFT(p.fecha_prestamo, 10) >= %s
                       GROUP BY l.id, l.titulo ORDER BY prestamos DESC, l.titulo LIMIT 5""", (inicio,))
        libros_top = cur.fetchall()

        cur.execute(f"""SELECT {NOMBRE_MIEMBRO} AS nombre, COUNT(*) AS prestamos
                        FROM prestamos p JOIN miembros m ON m.id = p.miembro_id
                        WHERE LEFT(p.fecha_prestamo, 10) >= %s
                        GROUP BY m.id, m.primer_nombre, m.primer_apellido
                        ORDER BY prestamos DESC LIMIT 3""", (inicio,))
        activos = cur.fetchall()

        # --- Multas ---
        cur.execute("""SELECT tipo_infraccion AS nombre, COUNT(*) AS n FROM multas
                       WHERE LEFT(fecha_inicio, 10) >= %s GROUP BY tipo_infraccion ORDER BY n DESC""", (inicio,))
        causales = _porcentajes(cur.fetchall(), 'causal')

        cur.execute("""SELECT COUNT(*) AS n, COALESCE(SUM(monto), 0) AS total
                       FROM multas WHERE estado = 'Activa'""")
        r = cur.fetchone()
        multas_activas, mora = r['n'], int(r['total'])
    finally:
        conn.close()

    a_tiempo, retrasadas = prestamos['tiempo'], prestamos['retrasadas']
    devueltos = a_tiempo + retrasadas
    tasa = f"{round(a_tiempo * 100 / devueltos)}%" if devueltos else '—'
    mora_txt = "${:,.0f}".format(mora)

    reports = {
        'kpis': [
            {'label': 'Libros (títulos)', 'valor': titulos, 'meta': f'{copias} ejemplares'},
            {'label': 'Miembros activos', 'valor': miembros_activos, 'meta': f'{miembros} registrados'},
            {'label': 'Préstamos', 'valor': prestamos['total'], 'meta': PERIODOS[period]},
            {'label': 'Mora por cobrar', 'valor': mora_txt, 'meta': f'{multas_activas} multa(s) activa(s)'},
        ],
        'inventario': {'total_ejemplares': copias, 'disponibles': disponibles,
                       'prestados': max(copias - disponibles, 0)},
        'libros_top': libros_top,
        'usuarios': {'adultos': miembros - menores, 'menores': menores,
                     'activos': activos, 'tipo_documento': tipo_documento},
        'prestamos': {'total': prestamos['total'], 'tiempo': a_tiempo,
                      'retrasadas': retrasadas, 'duracion': duracion},
        'multas': {'causales': causales},
        'resumen': {'stock': copias, 'miembros': miembros, 'tasa': tasa, 'mora': mora_txt},
    }
    return render_template('aplicacion/reportes.html', reports=reports, period=period)
