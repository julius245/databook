# Modulo para gestionar la conexion con PostgreSQL en Render
import os
import psycopg2
from urllib.parse import urlparse
from config import Config

def _connect():
    # Obtenemos la URL de conexion que configuramos en las variables de entorno de Render
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Si existe la URL completa de Render, nos conectamos usando parseo de URL
        url = urlparse(database_url)
        return psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    else:
        # Conexion de respaldo por si acaso usa variables separadas
        return psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        )

# Prueba la conexion a la base de datos al iniciar el servidor
def init_db():
    try:
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        conn.close()
        print("Base de datos PostgreSQL conectada exitosamente.")
    except Exception as e:
        print(f"Error al conectar con la base de datos PostgreSQL: {e}")
