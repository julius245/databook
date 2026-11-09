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
-- Autoreparacion: si la tabla ya existia con un esquema antiguo, CREATE TABLE
-- IF NOT EXISTS no agrega las columnas nuevas. Estas lineas las agregan.
-- =====================================================================
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS fecha_registro VARCHAR(50) NOT NULL DEFAULT to_char(now(), 'YYYY-MM-DD HH24:MI:SS');
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS rol VARCHAR(20) NOT NULL DEFAULT 'staff';
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS creado_por INT DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'Activo';
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS modulos_permitidos VARCHAR(255) NOT NULL DEFAULT 'catalogo,miembros,prestamos,multas';
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS password_temporal SMALLINT NOT NULL DEFAULT 0;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS password_actualizada_en VARCHAR(50) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS primer_nombre VARCHAR(100) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS segundo_nombre VARCHAR(100) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS primer_apellido VARCHAR(100) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS segundo_apellido VARCHAR(100) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS tipo_documento VARCHAR(50) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS numero_documento VARCHAR(50) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS telefono VARCHAR(50) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS direccion VARCHAR(255) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS rol_equipo VARCHAR(50) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS permiso_catalogo VARCHAR(20) NOT NULL DEFAULT 'control_total';
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS permiso_miembros VARCHAR(20) NOT NULL DEFAULT 'control_total';
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS permiso_prestamos VARCHAR(20) NOT NULL DEFAULT 'control_total';
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS permiso_multas VARCHAR(20) NOT NULL DEFAULT 'control_total';
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS tema VARCHAR(20) NOT NULL DEFAULT 'sistema';
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS reset_password_token VARCHAR(255) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS reset_password_expira VARCHAR(50) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS pais VARCHAR(100) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS ciudad VARCHAR(120) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS latitud VARCHAR(30) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS longitud VARCHAR(30) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS zona_horaria VARCHAR(80) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS foto_perfil VARCHAR(255) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS tutor_nombre VARCHAR(150) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS tutor_apellido VARCHAR(150) DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS tutor_documento VARCHAR(50) DEFAULT NULL;
ALTER TABLE libros ADD COLUMN IF NOT EXISTS isbn VARCHAR(50);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS categoria VARCHAR(100) NOT NULL DEFAULT 'General';
ALTER TABLE libros ADD COLUMN IF NOT EXISTS editorial VARCHAR(150);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS anio INT;
ALTER TABLE libros ADD COLUMN IF NOT EXISTS total_ejemplares INT NOT NULL DEFAULT 1;
ALTER TABLE libros ADD COLUMN IF NOT EXISTS disponibles INT NOT NULL DEFAULT 1;
ALTER TABLE libros ADD COLUMN IF NOT EXISTS ubicacion VARCHAR(100);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS descripcion TEXT;
ALTER TABLE libros ADD COLUMN IF NOT EXISTS portada VARCHAR(255);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS marc_control VARCHAR(50);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS marc_leader VARCHAR(24);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS marc_dewey VARCHAR(50);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS idioma VARCHAR(20);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS lugar_publicacion VARCHAR(150);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS tipo_material VARCHAR(80);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS edicion VARCHAR(100);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS paginas VARCHAR(50);
ALTER TABLE libros ADD COLUMN IF NOT EXISTS marc_json TEXT;
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS primer_nombre VARCHAR(100) NOT NULL DEFAULT '';
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS segundo_nombre VARCHAR(100);
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS primer_apellido VARCHAR(100) NOT NULL DEFAULT '';
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS segundo_apellido VARCHAR(100);
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS tipo VARCHAR(50) NOT NULL DEFAULT 'Estudiante';
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS email VARCHAR(150);
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS telefono VARCHAR(50);
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS direccion VARCHAR(255);
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS notas TEXT;
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS estado VARCHAR(30) NOT NULL DEFAULT 'Activo';
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS tutor_nombre VARCHAR(150);
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS tutor_apellido VARCHAR(150);
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS tutor_documento VARCHAR(50);
ALTER TABLE miembros ADD COLUMN IF NOT EXISTS fecha_registro VARCHAR(50);
ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS fecha_devuelto VARCHAR(50);
ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS observaciones TEXT;
ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS estado VARCHAR(30) NOT NULL DEFAULT 'Activo';
ALTER TABLE multas ADD COLUMN IF NOT EXISTS descripcion TEXT;
ALTER TABLE multas ADD COLUMN IF NOT EXISTS fecha_pago VARCHAR(50) DEFAULT NULL;
ALTER TABLE multas ADD COLUMN IF NOT EXISTS monto INT NOT NULL DEFAULT 0;
ALTER TABLE multas ADD COLUMN IF NOT EXISTS notas TEXT;
ALTER TABLE multas ADD COLUMN IF NOT EXISTS estado VARCHAR(30) NOT NULL DEFAULT 'Activa';
ALTER TABLE configuracion_biblioteca ADD COLUMN IF NOT EXISTS pais VARCHAR(100) NOT NULL DEFAULT '';
ALTER TABLE configuracion_biblioteca ADD COLUMN IF NOT EXISTS ciudad VARCHAR(120) NOT NULL DEFAULT '';
ALTER TABLE configuracion_biblioteca ADD COLUMN IF NOT EXISTS direccion VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE configuracion_biblioteca ADD COLUMN IF NOT EXISTS latitud VARCHAR(30) DEFAULT NULL;
ALTER TABLE configuracion_biblioteca ADD COLUMN IF NOT EXISTS longitud VARCHAR(30) DEFAULT NULL;
ALTER TABLE configuracion_biblioteca ADD COLUMN IF NOT EXISTS zona_horaria VARCHAR(80) DEFAULT NULL;
ALTER TABLE configuracion_biblioteca ADD COLUMN IF NOT EXISTS actualizado_en VARCHAR(50);
ALTER TABLE sanciones_pedagogicas ADD COLUMN IF NOT EXISTS descripcion TEXT;
ALTER TABLE sanciones_pedagogicas ADD COLUMN IF NOT EXISTS horas INT NOT NULL DEFAULT 0;
ALTER TABLE sanciones_pedagogicas ADD COLUMN IF NOT EXISTS fecha_limite VARCHAR(50) DEFAULT NULL;
ALTER TABLE sanciones_pedagogicas ADD COLUMN IF NOT EXISTS fecha_cumplimiento VARCHAR(50) DEFAULT NULL;
ALTER TABLE sanciones_pedagogicas ADD COLUMN IF NOT EXISTS notas TEXT;
ALTER TABLE sanciones_pedagogicas ADD COLUMN IF NOT EXISTS estado VARCHAR(30) NOT NULL DEFAULT 'Activa';

-- Las cuentas registradas antes como 'usuario' son duenas de su biblioteca ('staff').
UPDATE usuarios SET rol = 'staff' WHERE rol = 'usuario';

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