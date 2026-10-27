# ==========================================
# MÓDULO DE CONEXIÓN Y GESTIÓN DE BASE DE DATOS
# Compatible con PostgreSQL (Render y Local)
# ==========================================

import os
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse
from config import Config

# Ruta del esquema SQL (se ejecuta al arrancar; es idempotente)
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'sql', 'schema_postgres.sql')

def _connect():
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        url = urlparse(database_url)
        return psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port,
            # Render exige SSL en conexiones externas; si ya usas la URL interna, no estorba
            sslmode=os.getenv('DB_SSLMODE', 'prefer'),
            # Las filas se devuelven como diccionarios: user['email'], total['total'], etc.
            cursor_factory=psycopg2.extras.RealDictCursor
        )
    else:
        return psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT,
            cursor_factory=psycopg2.extras.RealDictCursor
        )

def init_db():
    """Verifica la conexion y crea todas las tablas que falten (CREATE TABLE IF NOT EXISTS)."""
    conn = None
    try:
        conn = _connect()
        with conn.cursor() as cursor:
            with open(SCHEMA_PATH, encoding='utf-8') as f:
                cursor.execute(f.read())
        conn.commit()
        print("¡Base de datos PostgreSQL conectada y tablas verificadas!")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error al inicializar la base de datos PostgreSQL: {e}")
        raise
    finally:
        if conn:
            conn.close()

def ejecutar_query(sql, params=None, fetch=False, fetchone=False):
    conn = None
    cursor = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
            
        if sql.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            conn.commit()
            
        resultado = None
        if fetch:
            resultado = cursor.fetchall()
        elif fetchone:
            resultado = cursor.fetchone()
            
        return resultado

    except Exception as e:
        print(f"Error ejecutando la consulta SQL: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()