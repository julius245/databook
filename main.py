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
            init_db() # Aqui se ejecutan las tablas e indices iniciales
            print("Base de datos conectada correctamente.")
        except Exception as e:
            print(f"Error al conectar la base de datos: {e}")

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