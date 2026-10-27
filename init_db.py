import os
import psycopg2
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()
database_url = os.getenv("DATABASE_URL")

try:
    print("Conectando a la base de datos de Render...")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    # Crear la tabla con los campos exactos que pide tu aplicación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
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
    print("¡Éxito! La tabla 'usuarios' ha sido creada correctamente en PostgreSQL.")
except Exception as e:
    print("Ocurrió un error al crear la tabla:", e) 