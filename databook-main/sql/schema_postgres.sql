-- =====================================================================
-- DataBook - Esquema PostgreSQL (idempotente: se puede ejecutar siempre)
-- Lo ejecuta automaticamente models/database.py -> init_db() al arrancar.
-- =====================================================================

CREATE TABLE IF NOT EXISTS usuarios (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(150) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  fecha_registro VARCHAR(50) NOT NULL DEFAULT to_char(now(), 'YYYY-MM-DD HH24:MI:SS'),
  rol VARCHAR(20) NOT NULL DEFAULT 'staff',
  creado_por INT DEFAULT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'Activo',
  modulos_permitidos VARCHAR(255) NOT NULL DEFAULT 'catalogo,miembros,prestamos,multas',
  password_temporal SMALLINT NOT NULL DEFAULT 0,
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
);

CREATE TABLE IF NOT EXISTS libros (
  id SERIAL PRIMARY KEY,
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
);

CREATE TABLE IF NOT EXISTS miembros (
  id SERIAL PRIMARY KEY,
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
);

CREATE TABLE IF NOT EXISTS prestamos (
  id SERIAL PRIMARY KEY,
  libro_id INT NOT NULL REFERENCES libros(id) ON DELETE CASCADE,
  miembro_id INT NOT NULL REFERENCES miembros(id) ON DELETE CASCADE,
  fecha_prestamo VARCHAR(50) NOT NULL,
  fecha_devolucion VARCHAR(50) NOT NULL,
  fecha_devuelto VARCHAR(50),
  observaciones TEXT,
  estado VARCHAR(30) NOT NULL DEFAULT 'Activo'
);

CREATE TABLE IF NOT EXISTS multas (
  id SERIAL PRIMARY KEY,
  prestamo_id INT NOT NULL REFERENCES prestamos(id) ON DELETE CASCADE,
  tipo_infraccion VARCHAR(100) NOT NULL,
  descripcion TEXT,
  fecha_inicio VARCHAR(50) NOT NULL,
  fecha_pago VARCHAR(50) DEFAULT NULL,
  monto INT NOT NULL DEFAULT 0,
  notas TEXT,
  estado VARCHAR(30) NOT NULL DEFAULT 'Activa'
);

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
);

CREATE TABLE IF NOT EXISTS sanciones_pedagogicas (
  id SERIAL PRIMARY KEY,
  prestamo_id INT DEFAULT NULL REFERENCES prestamos(id) ON DELETE SET NULL,
  miembro_id INT NOT NULL REFERENCES miembros(id) ON DELETE CASCADE,
  tipo VARCHAR(80) NOT NULL,
  descripcion TEXT,
  horas INT NOT NULL DEFAULT 0,
  fecha_inicio VARCHAR(50) NOT NULL,
  fecha_limite VARCHAR(50) DEFAULT NULL,
  fecha_cumplimiento VARCHAR(50) DEFAULT NULL,
  notas TEXT,
  estado VARCHAR(30) NOT NULL DEFAULT 'Activa'
);

CREATE TABLE IF NOT EXISTS notificaciones_prestamo (
  id SERIAL PRIMARY KEY,
  prestamo_id INT NOT NULL REFERENCES prestamos(id) ON DELETE CASCADE,
  tipo VARCHAR(30) NOT NULL,
  fecha_envio VARCHAR(50) NOT NULL
);

-- =====================================================================
-- Columnas de auditoria (usuario que creo/actualizo el registro).
-- ADD COLUMN IF NOT EXISTS: tambien actualiza bases ya creadas antes.
-- =====================================================================
ALTER TABLE configuracion_biblioteca ADD COLUMN IF NOT EXISTS actualizado_por INT
  REFERENCES usuarios(id) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE multas ADD COLUMN IF NOT EXISTS usuario_id INT
  REFERENCES usuarios(id) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE notificaciones_prestamo ADD COLUMN IF NOT EXISTS usuario_id INT
  REFERENCES usuarios(id) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS usuario_id INT
  REFERENCES usuarios(id) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE sanciones_pedagogicas ADD COLUMN IF NOT EXISTS usuario_id INT
  REFERENCES usuarios(id) ON DELETE SET NULL ON UPDATE CASCADE;

-- =====================================================================
-- Indices (los mismos de tu base MySQL)
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_configuracion_actualizado_por ON configuracion_biblioteca (actualizado_por);
CREATE INDEX IF NOT EXISTS idx_libros_titulo ON libros (titulo);
CREATE INDEX IF NOT EXISTS idx_libros_autor ON libros (autor);
CREATE INDEX IF NOT EXISTS idx_libros_isbn ON libros (isbn);
CREATE INDEX IF NOT EXISTS idx_libros_categoria ON libros (categoria);
CREATE INDEX IF NOT EXISTS idx_libros_disp ON libros (disponibles);
CREATE INDEX IF NOT EXISTS idx_miembros_nombre ON miembros (primer_apellido, primer_nombre);
CREATE INDEX IF NOT EXISTS idx_miembros_estado ON miembros (estado);
CREATE INDEX IF NOT EXISTS idx_multas_prestamo ON multas (prestamo_id);
CREATE INDEX IF NOT EXISTS idx_multas_estado ON multas (estado);
CREATE INDEX IF NOT EXISTS idx_multas_usuario ON multas (usuario_id);
CREATE INDEX IF NOT EXISTS idx_notificaciones_prestamo ON notificaciones_prestamo (prestamo_id);
CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON notificaciones_prestamo (usuario_id);
CREATE INDEX IF NOT EXISTS idx_prestamos_estado_dev ON prestamos (estado, fecha_devolucion);
CREATE INDEX IF NOT EXISTS idx_prestamos_libro_est ON prestamos (libro_id, estado);
CREATE INDEX IF NOT EXISTS idx_prestamos_miem_est ON prestamos (miembro_id, estado);
CREATE INDEX IF NOT EXISTS idx_prestamos_usuario ON prestamos (usuario_id);
CREATE INDEX IF NOT EXISTS idx_sanciones_miembro ON sanciones_pedagogicas (miembro_id);
CREATE INDEX IF NOT EXISTS idx_sanciones_prestamo ON sanciones_pedagogicas (prestamo_id);
CREATE INDEX IF NOT EXISTS idx_sanciones_usuario ON sanciones_pedagogicas (usuario_id);