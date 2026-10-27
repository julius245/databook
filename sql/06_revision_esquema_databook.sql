-- =====================================================================
-- Revisión de compatibilidad: base `databook` (e.sql) vs. esquema que crea la app
-- (versión corregida).
-- PARTE A: solo lectura (segura).
-- PARTE B: cambios. Cada paso es repetible y se omite solo si no aplica.
--          Haz respaldo y pruébala primero en una COPIA.
-- =====================================================================
SET NAMES utf8mb4;
USE `databook`;   -- <-- CAMBIA por tu base de biblioteca

-- ---------- PARTE A: diagnóstico (solo SELECT) ----------
SELECT 'libros: disponibles > total' AS chequeo, COUNT(*) AS filas FROM libros WHERE disponibles > total_ejemplares
UNION ALL SELECT 'libros: negativos', COUNT(*) FROM libros WHERE disponibles < 0 OR total_ejemplares < 0
UNION ALL SELECT 'libros: ISBN duplicado', COUNT(*) FROM (SELECT isbn FROM libros WHERE isbn IS NOT NULL AND isbn<>'' GROUP BY isbn HAVING COUNT(*)>1) d
UNION ALL SELECT 'prestamos huérfanos (libro)', COUNT(*) FROM prestamos p LEFT JOIN libros l ON l.id=p.libro_id WHERE l.id IS NULL
UNION ALL SELECT 'prestamos huérfanos (miembro)', COUNT(*) FROM prestamos p LEFT JOIN miembros m ON m.id=p.miembro_id WHERE m.id IS NULL
UNION ALL SELECT 'inventario descuadrado', COUNT(*) FROM libros l
  WHERE l.disponibles <> l.total_ejemplares - (SELECT COUNT(*) FROM prestamos p WHERE p.libro_id=l.id AND p.estado='Activo');

-- Columnas de `databook` que la app no crea ni usa: libros.edicion, libros.paginas (inofensivas).
-- Intercalación de cada tabla (deberían ser todas utf8mb4_unicode_ci):
SELECT table_name, table_collation FROM information_schema.tables WHERE table_schema = DATABASE();
-- Claves foráneas (hay duplicadas fk_* y *_ibfk_*):
SELECT table_name, constraint_name FROM information_schema.table_constraints
 WHERE table_schema = DATABASE() AND constraint_type='FOREIGN KEY' ORDER BY table_name, constraint_name;

-- ---------- PARTE B: correcciones ----------
-- 1) Misma intercalación en todas las tablas (evita "Illegal mix of collations").
ALTER TABLE configuracion_biblioteca CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE notificaciones_prestamo  CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE sanciones_pedagogicas    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2) Quitar FKs duplicadas. Solo se borra la copia fk_* si existe su gemela *_ibfk_*
--    (la app comprueba las *_ibfk_* por nombre, así que esas se conservan).
SET @s := IF(
  (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema=DATABASE() AND table_name='multas' AND constraint_name='fk_multas_prestamos' AND constraint_type='FOREIGN KEY') > 0
  AND (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema=DATABASE() AND table_name='multas' AND constraint_name='multas_ibfk_1' AND constraint_type='FOREIGN KEY') > 0,
  "ALTER TABLE multas DROP FOREIGN KEY fk_multas_prestamos",
  "SELECT 'multas: nada que quitar' AS aviso");
PREPARE p1 FROM @s; EXECUTE p1; DEALLOCATE PREPARE p1;

SET @s := IF(
  (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema=DATABASE() AND table_name='prestamos' AND constraint_name='fk_prestamos_libros' AND constraint_type='FOREIGN KEY') > 0
  AND (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema=DATABASE() AND table_name='prestamos' AND constraint_name='prestamos_ibfk_1' AND constraint_type='FOREIGN KEY') > 0,
  "ALTER TABLE prestamos DROP FOREIGN KEY fk_prestamos_libros",
  "SELECT 'prestamos/libros: nada que quitar' AS aviso");
PREPARE p2 FROM @s; EXECUTE p2; DEALLOCATE PREPARE p2;

SET @s := IF(
  (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema=DATABASE() AND table_name='prestamos' AND constraint_name='fk_prestamos_miembros' AND constraint_type='FOREIGN KEY') > 0
  AND (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema=DATABASE() AND table_name='prestamos' AND constraint_name='prestamos_ibfk_2' AND constraint_type='FOREIGN KEY') > 0,
  "ALTER TABLE prestamos DROP FOREIGN KEY fk_prestamos_miembros",
  "SELECT 'prestamos/miembros: nada que quitar' AS aviso");
PREPARE p3 FROM @s; EXECUTE p3; DEALLOCATE PREPARE p3;

-- 3) Integridad del inventario (CHECK). Solo se crea si aún no existe Y si ningún
--    libro la incumple hoy; si hay filas malas, corrígelas con la Parte A y repite.
SET @s := IF(
  (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema=DATABASE() AND table_name='libros' AND constraint_name='chk_libros_stock') = 0
  AND (SELECT COUNT(*) FROM libros WHERE total_ejemplares < 0 OR disponibles < 0 OR disponibles > total_ejemplares) = 0,
  "ALTER TABLE libros ADD CONSTRAINT chk_libros_stock CHECK (total_ejemplares >= 0 AND disponibles >= 0 AND disponibles <= total_ejemplares)",
  "SELECT 'CHECK de stock: ya existe o hay libros que la incumplen (ver Parte A)' AS aviso");
PREPARE p4 FROM @s; EXECUTE p4; DEALLOCATE PREPARE p4;

-- 4) `edicion` y `paginas`: se dejan tal cual (la app las ignora sin romperse).

-- 5) IMPORTANTE: la app solo abre bases llamadas `databook` (id en
--    databook.usuarios). `databook` no se usa hasta importarla a la base de un staff:
--    en phpMyAdmin crea databook (utf8mb4_unicode_ci), selecciónala y usa
--    la pestaña Importar con e.sql. Antes confirma tu id:
--      SELECT id, email, rol FROM databook.usuarios;
