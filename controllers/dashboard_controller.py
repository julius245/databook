# Controlador del dashboard del usuario
from datetime import date, datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, session, redirect, url_for
from models.database import _connect

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun',
         'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
UPCOMING_DAYS = 7      # ventana de "vencen pronto"
ACTIVITY_MONTHS = 6    # meses en la gráfica de barras
ZONA_POR_DEFECTO = 'America/Bogota'


def _hoy(cur):
    """Fecha de hoy en la zona horaria de la biblioteca (Render corre en UTC)."""
    zona = ZONA_POR_DEFECTO
    try:
        cur.execute("SELECT zona_horaria FROM configuracion_biblioteca LIMIT 1")
        fila = cur.fetchone()
        if fila and fila['zona_horaria']:
            zona = fila['zona_horaria']
    except Exception:
        cur.connection.rollback()   # Postgres deja la transacción abortada tras un error
    try:
        return datetime.now(ZoneInfo(zona)).date()
    except Exception:
        return date.today()


def _primer_dia_mes(hoy, meses_atras):
    n = hoy.month - 1 - meses_atras
    return date(hoy.year + n // 12, n % 12 + 1, 1)


# Carga la vista principal con indicadores rapidos
@dashboard_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = _connect()
    try:
        cur = conn.cursor()
        hoy = _hoy(cur)
        hoy_s = hoy.isoformat()          # 'YYYY-MM-DD': la plantilla lo compara como texto
        mes_actual = hoy_s[:7]
        limite_s = date.fromordinal(hoy.toordinal() + UPCOMING_DAYS).isoformat()

        # --- Libros y ejemplares ---
        cur.execute("""SELECT COUNT(*) AS n,
                              COALESCE(SUM(total_ejemplares), 0) AS copias,
                              COALESCE(SUM(disponibles), 0) AS disp
                       FROM libros""")
        r = cur.fetchone()
        total_books = r['n']
        total_copies = int(r['copias'])
        available_copies = int(r['disp'])
        borrowed_copies = max(total_copies - available_copies, 0)
        borrowed_percentage = round(borrowed_copies * 100 / total_copies) if total_copies else 0

        # --- Miembros ---
        cur.execute("SELECT COUNT(*) AS n FROM miembros WHERE estado = 'Activo'")
        active_members = cur.fetchone()['n']

        # --- Préstamos: activos, vencidos y devueltos este mes ---
        cur.execute("""SELECT
                         COUNT(*) FILTER (WHERE estado = 'Activo') AS activos,
                         COUNT(*) FILTER (WHERE estado = 'Activo'
                                          AND LEFT(fecha_devolucion, 10) < %s) AS vencidos,
                         COUNT(*) FILTER (WHERE estado = 'Devuelto'
                                          AND LEFT(COALESCE(fecha_devuelto, ''), 7) = %s) AS devueltos
                       FROM prestamos""", (hoy_s, mes_actual))
        r = cur.fetchone()
        active_loans, overdue, returned_this_month = r['activos'], r['vencidos'], r['devueltos']

        # --- Multas pendientes (la plantilla usa pending_fines.n y .total) ---
        cur.execute("""SELECT COUNT(*) AS n, COALESCE(SUM(monto), 0) AS total
                       FROM multas WHERE estado IN ('Activa', 'Pendiente')""")
        r = cur.fetchone()
        pending_fines = {'n': r['n'], 'total': int(r['total'])}

        # --- Préstamos por mes (últimos ACTIVITY_MONTHS meses) ---
        inicio = _primer_dia_mes(hoy, ACTIVITY_MONTHS - 1)
        cur.execute("""SELECT LEFT(fecha_prestamo, 7) AS mes, COUNT(*) AS n
                       FROM prestamos
                       WHERE LEFT(fecha_prestamo, 10) >= %s
                       GROUP BY 1""", (inicio.isoformat(),))
        por_mes = {f['mes']: f['n'] for f in cur.fetchall()}
        meses = [_primer_dia_mes(hoy, i) for i in range(ACTIVITY_MONTHS - 1, -1, -1)]
        maximo = max([por_mes.get(m.strftime('%Y-%m'), 0) for m in meses] + [1])
        activity = []
        for m in meses:
            clave = m.strftime('%Y-%m')
            total = por_mes.get(clave, 0)
            activity.append({
                'etiqueta': MESES[m.month - 1],
                'total': total,
                'alto': max(round(total * 100 / maximo), 4) if total else 0,
                'actual': clave == mes_actual,
            })
        total_activity = sum(a['total'] for a in activity)

        # --- Libros por categoría ---
        cur.execute("""SELECT categoria, COUNT(*) AS total FROM libros
                       GROUP BY categoria ORDER BY total DESC, categoria LIMIT 8""")
        books_by_category = cur.fetchall()

        # --- Más prestados ---
        cur.execute("""SELECT l.titulo, l.autor, COUNT(*) AS veces
                       FROM prestamos p JOIN libros l ON l.id = p.libro_id
                       GROUP BY l.id, l.titulo, l.autor
                       ORDER BY veces DESC, l.titulo LIMIT 5""")
        most_borrowed = cur.fetchall()

        # --- Vencen en los próximos días ---
        cur.execute("""SELECT l.titulo,
                              (m.primer_nombre || ' ' || m.primer_apellido) AS nombre_completo,
                              LEFT(p.fecha_devolucion, 10) AS fecha_devolucion
                       FROM prestamos p
                       JOIN libros l ON l.id = p.libro_id
                       JOIN miembros m ON m.id = p.miembro_id
                       WHERE p.estado = 'Activo'
                         AND LEFT(p.fecha_devolucion, 10) BETWEEN %s AND %s
                       ORDER BY p.fecha_devolucion LIMIT 8""", (hoy_s, limite_s))
        upcoming_due = cur.fetchall()

        # --- Préstamos recientes ---
        cur.execute("""SELECT l.titulo,
                              (m.primer_nombre || ' ' || m.primer_apellido) AS nombre_completo,
                              p.estado,
                              LEFT(p.fecha_devolucion, 10) AS fecha_devolucion
                       FROM prestamos p
                       JOIN libros l ON l.id = p.libro_id
                       JOIN miembros m ON m.id = p.miembro_id
                       ORDER BY p.id DESC LIMIT 5""")
        recent_loans = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        'aplicacion/dashboard.html',
        today=hoy_s,
        total_books=total_books,
        total_copies=total_copies,
        available_copies=available_copies,
        borrowed_copies=borrowed_copies,
        borrowed_percentage=borrowed_percentage,
        active_members=active_members,
        active_loans=active_loans,
        overdue=overdue,
        returned_this_month=returned_this_month,
        pending_fines=pending_fines,
        activity=activity,
        total_activity=total_activity,
        books_by_category=books_by_category,
        most_borrowed=most_borrowed,
        upcoming_days=UPCOMING_DAYS,
        upcoming_due=upcoming_due,
        recent_loans=recent_loans,
    )
