# DataBook — versión integrada

Aplicación web de gestión bibliotecaria construida con Flask, Jinja, CSS y MySQL/MariaDB.

## Contenido integrado
- Catálogo de libros, miembros, préstamos y devoluciones.
- Multas y sanciones pedagógicas.
- Gestión de usuarios, roles y permisos, panel de superadministración.
- Historial, reportes, configuración de biblioteca y notificaciones de préstamos.
- Protección CSRF, cookies de sesión seguras y cabeceras HTTP básicas.
- Migraciones SQL e índices de búsqueda.

## Requisitos
- Python 3.10 o superior (recomendado Python 3.11).
- MySQL o MariaDB y phpMyAdmin opcional para administrar la base de datos.

## Instalación local en Windows
1. Instala/abre MySQL o MariaDB. La aplicación usa una sola base llamada `databook` (no crea bases `databook_user_N`).
2. Abre una terminal en esta carpeta.
3. Crea un entorno virtual:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```
4. Instala dependencias:
   ```powershell
   pip install -r requirements.txt
   ```
5. Copia `.env.example` a `.env` y edita los datos de conexión. Para desarrollo local deja `APP_ENV=development` y `SESSION_COOKIE_SECURE=0`. Define `SECRET_KEY` con un valor aleatorio largo y `SUPERADMIN_PASSWORD` con al menos 12 caracteres.
6. En phpMyAdmin selecciona `databook` e importa `sql/01_migracion_v4.sql`. Este script crea tanto `usuarios` como `libros`, `miembros`, `prestamos`, `multas`, `configuracion_biblioteca`, `sanciones_pedagogicas` y `notificaciones_prestamo`.
7. Los demás scripts son complementarios y deben ejecutarse solo después de revisar su contenido y confirmar que las tablas existen: `02_limpiar_libros_default.sql` puede borrar datos de ejemplo; `03_direccion_biblioteca.sql` actualiza la dirección; `04_usuario_mysql_minimo.sql` es opcional y requiere revisar la contraseña; `05_indices_busqueda.sql` añade índices; `06_revision_esquema_databook.sql` es diagnóstico.
8. Inicia:
   ```powershell
   python main.py
   ```
9. Abre `http://127.0.0.1:5000`.

## Importante
- No se incluye `.env`, contraseñas, repositorio `.git`, bytecode ni volcados SQL completos con datos de la base. Usa tus propias credenciales.
- No ejecutes scripts de limpieza o corrección sobre producción sin respaldo.
- En producción cambia `APP_ENV=production`, genera una `SECRET_KEY` segura, usa un usuario MySQL con privilegios mínimos y configura HTTPS (`SESSION_COOKIE_SECURE=1`).
- Esta versión apunta todas las cuentas a una sola base `databook`. Si necesitas varias bibliotecas independientes con datos aislados entre sí, hace falta una separación por biblioteca a nivel de tablas/permisos; esta configuración compartida no proporciona aislamiento de datos entre cuentas.
- La integración se revisó mediante comprobación sintáctica de Python. No se ha probado contra tu servidor MySQL ni contra todas las rutas en ejecución.
