import os
import psycopg2
from psycopg2.extras import RealDictCursor

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta_por_defecto")
    DATABASE_URL = os.getenv("DATABASE_URL")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "databook")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))

def get_db_connection():
    """Establece la conexión con PostgreSQL usando diccionarios para los resultados"""
    conn = psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor  # <--- Esto es lo que soluciona el error de tuplas
    )
    return conn