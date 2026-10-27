-- =====================================================================
-- DataBook — Columna `direccion` en la base MAESTRA (versión corregida)
-- Se puede ejecutar varias veces: crea la base si falta y solo agrega la
-- columna si no existe. Si la tabla `usuarios` aún no existe, avisa
-- (ejecuta antes 01_migracion_v4.sql o inicia la app una vez).
-- La base maestra es `databook`.
-- =====================================================================
CREATE DATABASE IF NOT EXISTS `databook`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `databook`;

SET @tabla := (SELECT COUNT(*) FROM information_schema.tables
               WHERE table_schema = DATABASE() AND table_name = 'usuarios');
SET @col   := (SELECT COUNT(*) FROM information_schema.columns
               WHERE table_schema = DATABASE() AND table_name = 'usuarios'
                 AND column_name = 'direccion');

SET @sql := IF(@tabla = 0,
  "SELECT 'La tabla usuarios no existe: ejecuta primero 01_migracion_v4.sql o inicia la app' AS aviso",
  IF(@col = 0,
     "ALTER TABLE usuarios ADD COLUMN direccion VARCHAR(255) DEFAULT NULL",
     "SELECT 'La columna direccion ya existe' AS aviso"));
PREPARE paso FROM @sql;
EXECUTE paso;
DEALLOCATE PREPARE paso;
