"""Envío de correo reutilizable (recuperación de clave y alertas de préstamos)."""

import smtplib
from email.mime.text import MIMEText

from flask import current_app


def send_email(destination, subject, body):
    """Envía un correo de texto. Si no hay SMTP, deja el contenido en el log."""
    smtp_host = current_app.config.get("SMTP_HOST")
    if not smtp_host:
        current_app.logger.info(
            "[DataBook] SMTP no configurado. Correo para %s | %s\n%s",
            destination, subject, body,
        )
        return True

    try:
        message = MIMEText(body, "plain", "utf-8")
        message["Subject"] = subject
        message["From"] = current_app.config.get("SMTP_FROM") or destination
        message["To"] = destination

        with smtplib.SMTP(smtp_host, current_app.config.get("SMTP_PORT", 587), timeout=10) as server:
            server.starttls()
            smtp_user = current_app.config.get("SMTP_USER")
            smtp_password = current_app.config.get("SMTP_PASSWORD")
            if smtp_user:
                server.login(smtp_user, smtp_password)
            server.send_message(message)
        return True
    except Exception:
        current_app.logger.exception("No se pudo enviar correo a %s", destination)
        current_app.logger.info("[DataBook] Correo para %s | %s\n%s", destination, subject, body)
        return False
