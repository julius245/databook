# Modulo para gestionar la conexion y ejecutar consultas directas en la base de datos
import pymysql
from config import Config

# Establece la conexion con MySQL devolviendo registros en formato diccionario
def _connect(db_name=Config.DB_NAME):
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=db_name,
        port=Config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

# Prueba la conexion a la base de datos al iniciar el servidor
def init_db():
    try:
        conn = _connect()
        conn.close()
        print("Base de datos lista para operar.")
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
