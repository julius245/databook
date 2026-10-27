# ==========================================
# MÓDULO DE CONEXIÓN Y GESTIÓN DE BASE DE DATOS
# Compatible con PostgreSQL (Render y Local)
# ==========================================

import os
import psycopg
import psycopg2
from urllib.parse import urlparse
from config import Config

def _connect():
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        url = urlparse(database_url)
        return psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    else:
        return psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        )

def init_db():
    try:
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.close()
        conn.close()
        print("¡Base de datos PostgreSQL conectada exitosamente!")
    except Exception as e:
        print(f"Error al conectar con la base de datos PostgreSQL: {e}")

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