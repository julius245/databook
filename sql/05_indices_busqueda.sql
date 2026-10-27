-- =====================================================================
-- Índices para las consultas reales de DataBook (versión corregida).
-- Ejecutar sobre CADA base de biblioteca (`databook`).
-- Sintaxis MariaDB 10.4 (IF NOT EXISTS), la de tu servidor. En MySQL 8 quita
-- "IF NOT EXISTS" e ignora el error "Duplicate key name" si ya existe.
-- Haz respaldo antes. NO cambia el comportamiento de ninguna búsqueda.
-- =====================================================================
USE `databook`;   -- <-- CAMBIA por tu base de biblioteca

CREATE INDEX IF NOT EXISTS idx_libros_titulo     ON libros (titulo);
CREATE INDEX IF NOT EXISTS idx_libros_autor      ON libros (autor);
CREATE INDEX IF NOT EXISTS idx_libros_isbn       ON libros (isbn);
CREATE INDEX IF NOT EXISTS idx_libros_categoria  ON libros (categoria);
CREATE INDEX IF NOT EXISTS idx_libros_disp       ON libros (disponibles);

CREATE INDEX IF NOT EXISTS idx_miembros_nombre   ON miembros (primer_apellido, primer_nombre);
CREATE INDEX IF NOT EXISTS idx_miembros_estado   ON miembros (estado);

CREATE INDEX IF NOT EXISTS idx_prestamos_estado_dev ON prestamos (estado, fecha_devolucion);
CREATE INDEX IF NOT EXISTS idx_prestamos_libro_est  ON prestamos (libro_id, estado);
CREATE INDEX IF NOT EXISTS idx_prestamos_miem_est   ON prestamos (miembro_id, estado);

CREATE INDEX IF NOT EXISTS idx_multas_estado     ON multas (estado);

-- Ver los índices resultantes:
SHOW INDEX FROM libros;
SHOW INDEX FROM prestamos;

-- Qué acelera y qué no (revisa con EXPLAIN: columnas type, key, rows):
--   EXPLAIN SELECT * FROM prestamos WHERE estado='Activo' ORDER BY fecha_devolucion;  -- usa índice
--   EXPLAIN SELECT * FROM libros WHERE titulo LIKE 'harry%';    -- usa índice (prefijo)
--   EXPLAIN SELECT * FROM libros WHERE titulo LIKE '%harry%';   -- NO puede usar B-tree
-- La búsqueda por ISBN/documento de la app aplica REPLACE() a la columna, así
-- que tampoco usa índice; con ~15 000 libros sigue siendo rápida.
--
-- Búsqueda "contiene" en catálogos más grandes: FULLTEXT (probar primero en copia).
--   ALTER TABLE libros ADD FULLTEXT INDEX ft_libros (titulo, autor, categoria);
--   SELECT * FROM libros WHERE MATCH(titulo, autor, categoria) AGAINST ('texto*' IN BOOLEAN MODE);
-- Recomendación: mantener el LIKE actual como respaldo para términos cortos.
