-- =====================================================================
-- DataBook — Limpieza de los 3 libros de PRUEBA (versión corregida)
-- ---------------------------------------------------------------------
-- Borra SOLO esos 3 libros exactos (título + autor + ISBN, sin importar los
-- guiones del ISBN) y solo si NO tienen préstamos. No toca libros reales.
--
-- ANTES DE EJECUTAR:
--  1) Cambia el nombre en USE por tu base de biblioteca (en tu servidor hoy
--     existe `databook`; cuando importes a la app será databook).
--  2) Haz un respaldo (Exportar en phpMyAdmin).
--  3) Ejecuta el paso 1 (vista previa) y revisa antes de correr el paso 2.
-- =====================================================================

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;   -- compara bien los acentos
USE `databook`;                                         -- <-- CAMBIA por tu base

-- 1) Vista previa
SELECT l.id, l.titulo, l.autor, l.isbn,
       (SELECT COUNT(*) FROM prestamos p WHERE p.libro_id = l.id) AS prestamos
FROM libros l
WHERE (l.titulo = '1984'                 AND l.autor = 'George Orwell'          AND REPLACE(l.isbn,'-','') = '9780451524935')
   OR (l.titulo = 'Cosmos'               AND l.autor = 'Carl Sagan'             AND REPLACE(l.isbn,'-','') = '9780345539434')
   OR (l.titulo = 'Cien años de soledad' AND l.autor = 'Gabriel García Márquez' AND REPLACE(l.isbn,'-','') = '9780060883287');

-- 2) Borrado (solo los que no tienen préstamos)
DELETE l FROM libros l
WHERE ((l.titulo = '1984'                 AND l.autor = 'George Orwell'          AND REPLACE(l.isbn,'-','') = '9780451524935')
    OR (l.titulo = 'Cosmos'               AND l.autor = 'Carl Sagan'             AND REPLACE(l.isbn,'-','') = '9780345539434')
    OR (l.titulo = 'Cien años de soledad' AND l.autor = 'Gabriel García Márquez' AND REPLACE(l.isbn,'-','') = '9780060883287'))
  AND NOT EXISTS (SELECT 1 FROM prestamos p WHERE p.libro_id = l.id);

-- 3) Verificación
SELECT ROW_COUNT() AS libros_borrados;
SELECT COUNT(*) AS libros_restantes FROM libros;

-- ---------------------------------------------------------------------
-- OPCIONAL — dejar el catálogo COMPLETAMENTE vacío (¡DESTRUCTIVO!)
-- Borra TODOS los libros, préstamos y multas de esa base. Descomenta solo si
-- de verdad quieres empezar de cero (y con respaldo hecho).
-- ---------------------------------------------------------------------
-- SET FOREIGN_KEY_CHECKS = 0;
-- DELETE FROM multas;
-- DELETE FROM prestamos;
-- DELETE FROM libros;
-- ALTER TABLE libros AUTO_INCREMENT = 1;
-- SET FOREIGN_KEY_CHECKS = 1;
