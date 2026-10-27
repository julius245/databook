import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_URL")

try:
    print("Conectando a la base de datos de Render...")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    # Recrear la tabla para asegurar todas las columnas necesarias
    cursor.execute("DROP TABLE IF EXISTS usuarios CASCADE;")
    cursor.execute("""
        CREATE TABLE usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100),
            primer_nombre VARCHAR(100),
            segundo_nombre VARCHAR(100),
            primer_apellido VARCHAR(100),
            segundo_apellido VARCHAR(100),
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(50) DEFAULT 'usuario',
            pais VARCHAR(100),
            zona_horaria VARCHAR(100)
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("¡Éxito! La tabla 'usuarios' ha sido recreada con todas las columnas.")
except Exception as e:
    print("Ocurrió un error al recrear la tabla:", e)