import os
from psycopg2.extras import RealDictCursor

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta_por_defecto")
    DATABASE_URL = os.getenv("DATABASE_URL")

# Si además tienes tu función de conexión aquí mismo, déjala lista con RealDictCursor:
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor
    )
    return conn