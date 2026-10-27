import os
import psycopg2
from psycopg2.extras import RealDictCursor # <--- 1. Importa esto

def get_db_connection():
    conn = psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor  # <--- 2. Agrégalo aquí dentro del connect
    )
    return conn