# En este archivo definimos las variables de entorno y datos de conexion a la base de datos
import os

class Config:
    # Clave secreta requerida por Flask para cifrar las cookies de sesion
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave_secreta_databook_2026')
    
    # Credenciales para la base de datos
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'databook')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
