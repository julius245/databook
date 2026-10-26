-- Ejecuta este archivo primero en phpMyAdmin si todavía no existe la base.
CREATE DATABASE IF NOT EXISTS `databook`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `databook`;
-- Después importa sql/01_migracion_v4.sql para crear usuarios y tablas operativas.
