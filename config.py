import os
import psycopg2
from psycopg2.extras import RealDictCursor

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta_por_defecto")
    DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Establece la conexión con PostgreSQL usando diccionarios para los resultados"""
    conn = psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor  # <--- Esto es lo que soluciona el error de tuplas
    )
    return conn