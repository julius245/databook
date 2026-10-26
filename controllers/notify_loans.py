"""Alertas de préstamos próximos a vencer o ya vencidos."""

from datetime import date, timedelta

from flask import current_app

from config import Config
from models.database import (
    get_connection,
    get_master_connection,
    user_db_name,
    migrate_library_schema,
)
from controllers.mail_utils import send_email

_FULL_NAME_SQL = (
    "TRIM(CONCAT_WS(' ', m.primer_nombre, m.segundo_nombre, m.primer_apellido, m.segundo_apellido))"
)

NOTICE_SOON = "proximo"
NOTICE_OVERDUE = "vencido"


def _iso_today():
    return date.today().isoformat()


def _days_until(due_text):
    try:
        due = date.fromisoformat(str(due_text)[:10])
    except (TypeError, ValueError):
        return None
    return (due - date.today()).days


def _already_sent(conn, loan_id, kind, on_date):
    row = conn.execute(
        """SELECT id FROM notificaciones_prestamo
           WHERE prestamo_id = ? AND tipo = ? AND fecha_envio = ?""",
        (loan_id, kind, on_date),
    ).fetchone()
    return bool(row)


def _mark_sent(conn, loan_id, kind, on_date):
    conn.execute(
        """INSERT INTO notificaciones_prestamo (prestamo_id, tipo, fecha_envio)
           VALUES (?, ?, ?)""",
        (loan_id, kind, on_date),
    )


def _notify_library(db_name, library_name):
    migrate_library_schema(db_name)
    conn = get_connection(db_name=db_name)
    today_iso = _iso_today()
    soon_limit = (date.today() + timedelta(days=2)).isoformat()

    loans = conn.execute(
        f"""SELECT p.id, p.fecha_devolucion, l.titulo,
                  {_FULL_NAME_SQL} AS miembro_nombre, m.email
           FROM prestamos p
           JOIN libros l ON l.id = p.libro_id
           JOIN miembros m ON m.id = p.miembro_id
           WHERE p.estado = 'Activo'
             AND m.email IS NOT NULL AND m.email <> ''"""
    ).fetchall()

    sent = skipped = 0
    for loan in loans:
        days = _days_until(loan["fecha_devolucion"])
        if days is None:
            continue
        if days < 0:
            kind = NOTICE_OVERDUE
            subject = f"Préstamo vencido — {library_name}"
            body = (
                f"Hola {loan['miembro_nombre']},\n\n"
                f"El préstamo de «{loan['titulo']}» venció el {loan['fecha_devolucion']}.\n"
                "Por favor devuélvelo lo antes posible para evitar o detener una multa.\n\n"
                f"{library_name}\n{Config.APP_NAME}"
            )
        elif loan["fecha_devolucion"] <= soon_limit:
            kind = NOTICE_SOON
            subject = f"Tu préstamo vence pronto — {library_name}"
            body = (
                f"Hola {loan['miembro_nombre']},\n\n"
                f"El préstamo de «{loan['titulo']}» vence el {loan['fecha_devolucion']}.\n"
                "Recuerda devolverlo a tiempo.\n\n"
                f"{library_name}\n{Config.APP_NAME}"
            )
        else:
            continue

        if _already_sent(conn, loan["id"], kind, today_iso):
            skipped += 1
            continue

        if send_email(loan["email"], subject, body):
            _mark_sent(conn, loan["id"], kind, today_iso)
            sent += 1

    conn.commit()
    conn.close()
    return sent, skipped


def notify_all_libraries():
    """Recorre cada biblioteca staff y envía las alertas pendientes de hoy."""
    master = get_master_connection()
    staff_rows = master.execute(
        "SELECT id, nombre FROM usuarios WHERE rol = 'staff' AND estado = 'Activo'"
    ).fetchall()
    master.close()

    total_sent = total_skipped = 0
    for staff in staff_rows:
        db_name = user_db_name(staff["id"])
        try:
            sent, skipped = _notify_library(db_name, staff["nombre"])
            total_sent += sent
            total_skipped += skipped
        except Exception:
            current_app.logger.exception("No se pudieron notificar préstamos de %s", db_name)
    return total_sent, total_skipped


def notify_current_library(library_name):
    """Envía alertas solo para la biblioteca de la sesión actual."""
    conn = get_connection()
    db_name = conn.execute("SELECT DATABASE() AS db").fetchone()["db"]
    conn.close()
    return _notify_library(db_name, library_name)
