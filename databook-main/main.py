# Hola, este es el archivo principal donde arranca toda la aplicacion web de Flask.
# Aqui conectamos las configuraciones, la base de datos y los controladores.

from flask import Flask, render_template, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from config import Config
from models.database import init_db
import os

# Esta funcion arma y configura nuestra aplicacion web

def create_app():
    # Inicializamos Flask indicando donde estan nuestras plantillas HTML y archivos estaticos
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Cargamos los parametros de configuracion desde la clase Config
    app.config.from_object(Config)
    
    # Inicializamos la proteccion CSRF vinculándola a la aplicación Flask
    csrf = CSRFProtect(app)
    
    # Verificamos e inicializamos la conexion a la base de datos al arrancar
    with app.app_context():
        try:
            init_db() # Crea las tablas si no existen (sql/schema_postgres.sql)
        except Exception as e:
            print(f"No se pudo inicializar la base de datos: {e}")

    # Filtro personalizado para solucionar el error de 'format_date' en el dashboard
    @app.template_filter('format_date')
    def format_date(value):
        if not value:
            return ""
        return str(value)

    # Funcion global disponible en todas las plantillas Jinja.
    # NOTA: el 'or True' permite todo; no aplica restricciones reales de permisos.
    @app.template_global()
    def has_permission(modulo, nivel):
        return session.get('user_role') == 'admin' or True

    # Importamos los controladores que manejan cada seccion del sistema
    from controllers.auth_controller import auth_bp
    from controllers.book_controller import book_bp
    from controllers.dashboard_controller import dashboard_bp
    from controllers.member_controller import member_bp
    from controllers.loan_controller import loan_bp
    from controllers.fine_controller import fine_bp
    from controllers.reports_controller import reports_bp
    from controllers.sanction_controller import sanction_controller
    from controllers.superadmin_controller import superadmin_bp
    from controllers.history_controller import history_bp
    from controllers.team_controller import team_bp

    # Registramos los blueprints para activar todas las rutas del sitio web
    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(loan_bp)
    app.register_blueprint(fine_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(sanction_controller)
    app.register_blueprint(superadmin_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(team_bp)

    # Alias de compatibilidad para nombres antiguos usados en algunas plantillas.
    # Las vistas principales ya tienen nombres canónicos, por lo que estos alias
    # evitan BuildError si una plantilla antigua todavía los referencia.
    aliases = {
        'books.catalog': 'books.list_books',
        'loans.loans': 'loans.list_loans',
        'members.members': 'members.list_members',
        'fines.fines': 'fines.list_fines',
        'sanctions.sanctions': 'sanctions.index',
        'history.history': 'history.index',
        'reports.reports': 'reports.index',
        'team.team': 'team.index',
        'superadmin.panel': 'superadmin.index',
    }
    for alias, target in aliases.items():
        if target in app.view_functions and alias not in app.view_functions:
            app.add_url_rule(
                f'/_compat/{alias.replace(".", "/")}',
                endpoint=alias,
                view_func=app.view_functions[target],
                methods=['GET'],
            )

    # Endpoints que las plantillas referencian, pero que aún no tienen lógica
    # de negocio implementada en los controladores. Se registran de forma segura
    # para que las páginas no fallen al renderizar con BuildError. Al usarlos,
    # se informa que la acción sigue pendiente y se vuelve a la sección adecuada.
    pendientes = {
        'auth.api_forgot_password',
        'auth.change_my_password',
        'auth.edit_my_library',
        'auth.edit_my_profile',
        'auth.reset_password',
        'auth.save_theme',
        'books.books_template',
        'books.delete_book',
        'books.export_books',
        'books.import_books',
        'fines.activate_fine',
        'fines.cancel_fine',
        'fines.pay_fine',
        'loans.new_loan',
        'loans.return_loan',
        'loans.send_notifications',
        'members.export_members',
        'members.import_members',
        'members.members_template',
        'members.new_member',
        'sanctions.cancel_sanction',
        'sanctions.complete_sanction',
        'sanctions.new_sanction',
        'superadmin.delete_staff',
        'superadmin.restrict_staff',
        'team.delete_librarian',
        'team.edit_librarian',
        'team.librarian_permissions',
        'team.new_librarian',
        'team.require_password_change',
        'team.reset_librarian_password',
        'team.restrict_librarian',
    }

    def accion_pendiente():
        from flask import request
        from flask import flash as flash_message
        flash_message(
            'Esta acción todavía no está implementada en el servidor.',
            'warning'
        )
        endpoint = request.endpoint or ''
        destino = {
            'books': 'books.list_books',
            'members': 'members.list_members',
            'loans': 'loans.list_loans',
            'fines': 'fines.list_fines',
            'sanctions': 'sanctions.index',
            'team': 'team.index',
            'superadmin': 'superadmin.index',
            'auth': 'auth.settings',
        }.get(endpoint.split('.', 1)[0], 'dashboard.index')
        return redirect(url_for(destino))

    for endpoint in pendientes:
        if endpoint not in app.view_functions:
            slug = endpoint.replace('.', '-').replace('_', '-')
            app.add_url_rule(
                f'/_pendiente/{slug}',
                endpoint=endpoint,
                view_func=accion_pendiente,
                methods=['GET', 'POST'],
            )

   # Ruta raiz del proyecto: cuando alguien entra al dominio los manda al inicio
    @app.route('/')
    def index():
        return render_template('web/index.html')

    return app

# Se crea la aplicacion principal para Gunicorn y producción
app = create_app()

# Para ejecutar el servidor local en modo desarrollo
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)