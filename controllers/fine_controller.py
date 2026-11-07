# Controlador de multas registradas por atraso
import os

from flask import Blueprint, render_template, request, session, redirect, url_for
from models.database import _connect
from controllers.dashboard_controller import _hoy

fine_bp = Blueprint('fines', __name__, url_prefix='/multas')

# Tarifa por día de mora (COP). Se puede cambiar con la variable de entorno MULTA_DIARIA en Render.
DAILY_FEE = int(os.getenv('MULTA_DIARIA', '1000'))
LATE_RETURN_INFRACTION = 'Préstamo vencido'
ESTADOS = ('Todas', 'Activa', 'Pagada', 'Cancelada')

NOMBRE_MIEMBRO = "(m.primer_nombre || ' ' || m.primer_apellido)"


@fine_bp.route('/')
def list_fines():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    search_term = request.args.get('q', '').strip()
    filter_value = request.args.get('estado', 'Todas')
    if filter_value not in ESTADOS:
        filter_value = 'Todas'

    # Filtros opcionales (los valores siempre van como parámetros, nunca dentro del SQL)
    where, params = [], []
    if filter_value != 'Todas':
        where.append("f.estado = %s")
        params.append(filter_value)
    if search_term:
        like = f"%{search_term}%"
        where.append(f"({NOMBRE_MIEMBRO} ILIKE %s OR m.documento_id ILIKE %s "
                     "OR l.titulo ILIKE %s OR COALESCE(l.isbn, '') ILIKE %s)")
        params += [like, like, like, like]
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    conn = _connect()
    try:
        cur = conn.cursor()
        hoy = _hoy(cur).isoformat()

        cur.execute(f"""SELECT f.id, f.tipo_infraccion, f.descripcion, f.monto, f.estado,
                               {NOMBRE_MIEMBRO} AS miembro_nombre,
                               m.documento_id, l.titulo AS libro_titulo, l.isbn
                        FROM multas f
                        JOIN prestamos p ON p.id = f.prestamo_id
                        JOIN miembros m ON m.id = p.miembro_id
                        JOIN libros l ON l.id = p.libro_id
                        {where_sql}
                        ORDER BY f.fecha_inicio DESC, f.id DESC""", params)
        fines = cur.fetchall()

        cur.execute("SELECT COUNT(*) AS n FROM multas WHERE estado = 'Activa'")
        total_active = cur.fetchone()['n']

        # Préstamos vencidos que todavía no tienen una multa activa (para el modal "Activar Multa")
        cur.execute(f"""SELECT p.id, l.titulo, {NOMBRE_MIEMBRO} AS nombre_completo,
                               LEFT(p.fecha_devolucion, 10) AS fecha_devolucion
                        FROM prestamos p
                        JOIN libros l ON l.id = p.libro_id
                        JOIN miembros m ON m.id = p.miembro_id
                        WHERE p.estado = 'Activo'
                          AND LEFT(p.fecha_devolucion, 10) < %s
                          AND NOT EXISTS (SELECT 1 FROM multas f
                                          WHERE f.prestamo_id = p.id AND f.estado = 'Activa')
                        ORDER BY p.fecha_devolucion""", (hoy,))
        overdue_loans = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        'aplicacion/multas.html',
        fines=fines,
        overdue_loans=overdue_loans,
        total_active=total_active,
        daily_fee=DAILY_FEE,
        late_return_infraction=LATE_RETURN_INFRACTION,
        search_term=search_term,
        filter_value=filter_value,
        today=hoy,
    )
