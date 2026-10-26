-- =====================================================================
-- Usuario de MySQL/MariaDB con privilegios mínimos para DataBook
-- (versión corregida). Ejecutar como root UNA vez.
--
-- >>> ANTES: reemplaza CAMBIA_ESTA_CLAVE_LARGA_Y_UNICA (las 2 veces) por una
-- >>> contraseña propia. Si lo ejecutas tal cual, queda una clave conocida.
--
-- La app crea/elimina bases `databook` y usa la maestra `databook`, por eso
-- necesita DDL solo sobre esas bases, nada global (sin GRANT OPTION, sin
-- acceso a mysql.* ni a otras bases como `databook` o `q`).
-- =====================================================================
CREATE USER IF NOT EXISTS 'databook_app'@'localhost'  IDENTIFIED BY 'CAMBIA_ESTA_CLAVE_LARGA_Y_UNICA';
CREATE USER IF NOT EXISTS 'databook_app'@'127.0.0.1'  IDENTIFIED BY 'CAMBIA_ESTA_CLAVE_LARGA_Y_UNICA';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX, REFERENCES
  ON `databook`.*                 TO 'databook_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX, REFERENCES
  ON `databook\_user\_%`.* TO 'databook_app'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX, REFERENCES
  ON `databook`.*                 TO 'databook_app'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX, REFERENCES
  ON `databook\_user\_%`.* TO 'databook_app'@'127.0.0.1';

FLUSH PRIVILEGES;

-- Comprobar:  SHOW GRANTS FOR 'databook_app'@'localhost';
-- Variables de entorno de la app:  DB_USER=databook_app  DB_PASSWORD=<tu clave>
-- DB_NAME debe ser `databook` (la maestra).
-- Cuando confirmes que funciona, deja de usar root en la app.
