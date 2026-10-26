-- =====================================================================
-- DataBook — Base MAESTRA `databook` (tabla `usuarios`) — versión corregida
-- Se puede ejecutar varias veces. Crea la base y la tabla si faltan y
-- agrega la columna `tema` solo si no existe.
-- =====================================================================
CREATE DATABASE IF NOT EXISTS `databook`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `databook`;

CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(150) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  fecha_registro VARCHAR(50) NOT NULL,
  rol VARCHAR(20) NOT NULL DEFAULT 'staff',
  creado_por INT DEFAULT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'Activo',
  modulos_permitidos VARCHAR(255) NOT NULL DEFAULT 'catalogo,miembros,prestamos,multas',
  password_temporal TINYINT(1) NOT NULL DEFAULT 0,
  password_actualizada_en VARCHAR(50) DEFAULT NULL,
  primer_nombre VARCHAR(100) DEFAULT NULL,
  segundo_nombre VARCHAR(100) DEFAULT NULL,
  primer_apellido VARCHAR(100) DEFAULT NULL,
  segundo_apellido VARCHAR(100) DEFAULT NULL,
  tipo_documento VARCHAR(50) DEFAULT NULL,
  numero_documento VARCHAR(50) DEFAULT NULL,
  telefono VARCHAR(50) DEFAULT NULL,
  direccion VARCHAR(255) DEFAULT NULL,
  rol_equipo VARCHAR(50) DEFAULT NULL,
  permiso_catalogo VARCHAR(20) NOT NULL DEFAULT 'control_total',
  permiso_miembros VARCHAR(20) NOT NULL DEFAULT 'control_total',
  permiso_prestamos VARCHAR(20) NOT NULL DEFAULT 'control_total',
  permiso_multas VARCHAR(20) NOT NULL DEFAULT 'control_total',
  tema VARCHAR(20) NOT NULL DEFAULT 'sistema',
  reset_password_token VARCHAR(255) DEFAULT NULL,
  reset_password_expira VARCHAR(50) DEFAULT NULL,
  pais VARCHAR(100) DEFAULT NULL,
  ciudad VARCHAR(120) DEFAULT NULL,
  latitud VARCHAR(30) DEFAULT NULL,
  longitud VARCHAR(30) DEFAULT NULL,
  zona_horaria VARCHAR(80) DEFAULT NULL,
  foto_perfil VARCHAR(255) DEFAULT NULL,
  tutor_nombre VARCHAR(150) DEFAULT NULL,
  tutor_apellido VARCHAR(150) DEFAULT NULL,
  tutor_documento VARCHAR(50) DEFAULT NULL
) ENGINE=InnoDB;

SET @existe := (SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = 'usuarios' AND column_name = 'tema');
SET @sql := IF(@existe = 0,
  "ALTER TABLE usuarios ADD COLUMN tema VARCHAR(20) NOT NULL DEFAULT 'sistema'",
  "SELECT 'La columna tema ya existe' AS aviso");
PREPARE paso FROM @sql;
EXECUTE paso;
DEALLOCATE PREPARE paso;

UPDATE usuarios SET tema = 'sistema' WHERE tema NOT IN ('claro', 'oscuro', 'sistema');

SELECT id, nombre, rol, tema FROM usuarios ORDER BY id;

-- =====================================================================
-- Tablas operativas de DataBook. Todas se crean en la única base `databook`.
-- CREATE TABLE IF NOT EXISTS conserva los datos que ya existan.
-- =====================================================================
CREATE TABLE IF NOT EXISTS libros (
  id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255) NOT NULL,
  autor VARCHAR(255) NOT NULL,
  isbn VARCHAR(50),
  categoria VARCHAR(100) NOT NULL DEFAULT 'General',
  editorial VARCHAR(150),
  anio INT,
  total_ejemplares INT NOT NULL DEFAULT 1,
  disponibles INT NOT NULL DEFAULT 1,
  ubicacion VARCHAR(100),
  descripcion TEXT,
  portada VARCHAR(255),
  marc_control VARCHAR(50),
  marc_leader VARCHAR(24),
  marc_dewey VARCHAR(50),
  idioma VARCHAR(20),
  lugar_publicacion VARCHAR(150),
  tipo_material VARCHAR(80),
  edicion VARCHAR(100),
  paginas VARCHAR(50),
  marc_json TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS miembros (
  id INT AUTO_INCREMENT PRIMARY KEY,
  primer_nombre VARCHAR(100) NOT NULL DEFAULT '',
  segundo_nombre VARCHAR(100),
  primer_apellido VARCHAR(100) NOT NULL DEFAULT '',
  segundo_apellido VARCHAR(100),
  documento_id VARCHAR(50) NOT NULL UNIQUE,
  tipo VARCHAR(50) NOT NULL DEFAULT 'Estudiante',
  email VARCHAR(150),
  telefono VARCHAR(50),
  direccion VARCHAR(255),
  notas TEXT,
  estado VARCHAR(30) NOT NULL DEFAULT 'Activo',
  tutor_nombre VARCHAR(150),
  tutor_apellido VARCHAR(150),
  tutor_documento VARCHAR(50),
  fecha_registro VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS prestamos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  libro_id INT NOT NULL,
  miembro_id INT NOT NULL,
  fecha_prestamo VARCHAR(50) NOT NULL,
  fecha_devolucion VARCHAR(50) NOT NULL,
  fecha_devuelto VARCHAR(50),
  observaciones TEXT,
  estado VARCHAR(30) NOT NULL DEFAULT 'Activo',
  CONSTRAINT fk_prestamos_libro FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE CASCADE,
  CONSTRAINT fk_prestamos_miembro FOREIGN KEY (miembro_id) REFERENCES miembros(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS multas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  prestamo_id INT NOT NULL,
  tipo_infraccion VARCHAR(100) NOT NULL,
  descripcion TEXT,
  fecha_inicio VARCHAR(50) NOT NULL,
  fecha_pago VARCHAR(50) DEFAULT NULL,
  monto INT NOT NULL DEFAULT 0,
  notas TEXT,
  estado VARCHAR(30) NOT NULL DEFAULT 'Activa',
  CONSTRAINT fk_multas_prestamo FOREIGN KEY (prestamo_id) REFERENCES prestamos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS configuracion_biblioteca (
  id INT PRIMARY KEY,
  nombre VARCHAR(150) NOT NULL,
  pais VARCHAR(100) NOT NULL DEFAULT '',
  ciudad VARCHAR(120) NOT NULL DEFAULT '',
  direccion VARCHAR(255) NOT NULL DEFAULT '',
  latitud VARCHAR(30) DEFAULT NULL,
  longitud VARCHAR(30) DEFAULT NULL,
  zona_horaria VARCHAR(80) DEFAULT NULL,
  actualizado_en VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sanciones_pedagogicas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  prestamo_id INT DEFAULT NULL,
  miembro_id INT NOT NULL,
  tipo VARCHAR(80) NOT NULL,
  descripcion TEXT,
  horas INT NOT NULL DEFAULT 0,
  fecha_inicio VARCHAR(50) NOT NULL,
  fecha_limite VARCHAR(50) DEFAULT NULL,
  fecha_cumplimiento VARCHAR(50) DEFAULT NULL,
  notas TEXT,
  estado VARCHAR(30) NOT NULL DEFAULT 'Activa',
  CONSTRAINT fk_sanciones_miembro FOREIGN KEY (miembro_id) REFERENCES miembros(id) ON DELETE CASCADE,
  CONSTRAINT fk_sanciones_prestamo FOREIGN KEY (prestamo_id) REFERENCES prestamos(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS notificaciones_prestamo (
  id INT AUTO_INCREMENT PRIMARY KEY,
  prestamo_id INT NOT NULL,
  tipo VARCHAR(30) NOT NULL,
  fecha_envio VARCHAR(50) NOT NULL,
  CONSTRAINT fk_notificaciones_prestamo FOREIGN KEY (prestamo_id) REFERENCES prestamos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'Estructura de DataBook creada en databook' AS resultado;
