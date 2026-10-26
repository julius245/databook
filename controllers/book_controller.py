# Controlador para la gestion de libros de la biblioteca
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import _connect

book_bp = Blueprint('books', __name__, url_prefix='/libros')

# Muestra el listado de libros
@book_bp.route('/')
def list_books():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM libros ORDER BY id DESC")
    books = cursor.fetchall()
    conn.close()
    return render_template('aplicacion/libros.html', libros=books)

# Registra un libro nuevo en la base de datos
@book_bp.route('/agregar', methods=['POST'])
def add_book():
    titulo = request.form.get('titulo')
    autor = request.form.get('autor')
    
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO libros (titulo, autor) VALUES (%s, %s)", (titulo, autor))
    conn.commit()
    conn.close()
    
    flash("Libro registrado", "success")
    return redirect(url_for('books.list_books'))
