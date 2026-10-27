# Controlador para la gestión de libros de la biblioteca

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.database import _connect

book_bp = Blueprint('books', __name__, url_prefix='/libros')


# Muestra el listado de libros (Cambiado a 'catalog' para que coincida con layout.html)
@book_bp.route('/', methods=['GET'])
def catalog():
    conn = None

    try:
        conn = _connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM libros ORDER BY id DESC")
        books = cursor.fetchall()

        return render_template(
            'aplicacion/libros.html',
            libros=books
        )

    except Exception:
        flash("No fue posible cargar el catálogo de libros.", "danger")
        raise

    finally:
        if conn is not None:
            conn.close()


# Registra un libro nuevo en la base de datos
@book_bp.route('/agregar', methods=['POST'])
def add_book():
    titulo = (request.form.get('titulo') or '').strip()
    autor = (request.form.get('autor') or '').strip()

    # Validación de los campos
    if not titulo or not autor:
        flash("Debes ingresar el título y el autor del libro.", "warning")
        return redirect(url_for('books.catalog'))

    conn = None

    try:
        conn = _connect()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO libros (titulo, autor) VALUES (%s, %s)",
            (titulo, autor)
        )

        conn.commit()

        flash("Libro registrado correctamente.", "success")

    except Exception:
        if conn is not None:
            conn.rollback()

        flash("No fue posible registrar el libro.", "danger")

    finally:
        if conn is not None:
            conn.close()

    return redirect(url_for('books.catalog'))