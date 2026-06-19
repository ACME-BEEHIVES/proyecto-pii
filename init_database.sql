-- init_database.sql
-- Script de inicialización de la base de datos para UpShield Edge Agent
-- Compatible con MySQL 8.0+

CREATE DATABASE IF NOT EXISTS pii_discovery CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pii_discovery;

-- -----------------------------------------------------
-- Table scan_jobs
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS scan_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    root_path VARCHAR(1024) NULL,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    files_total INT NOT NULL DEFAULT 0,
    files_scanned INT NOT NULL DEFAULT 0,
    files_skipped INT NOT NULL DEFAULT 0,
    findings_count INT NOT NULL DEFAULT 0,
    error_message TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table control_archivos
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS control_archivos (
    hash_ruta VARCHAR(64) NOT NULL PRIMARY KEY,
    archivo_nombre TEXT NULL,
    hash_archivo VARCHAR(64) NULL,
    ultima_actualizacion DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_archivo_nombre (archivo_nombre(255)),
    INDEX idx_hash_archivo (hash_archivo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table hallazgos
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS hallazgos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scan_job_id INT NULL,
    archivo_nombre TEXT NULL,
    file_name VARCHAR(255) NULL,
    tipo_entidad VARCHAR(50) NULL,
    texto_detectado TEXT NULL,
    puntaje_certeza FLOAT NULL,
    is_sensitive BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME NULL,
    resolved_by VARCHAR(100) DEFAULT NULL,
    resolution_method VARCHAR(50) DEFAULT NULL,
    resolution_notes TEXT DEFAULT NULL,
    fecha_deteccion DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_job_id) REFERENCES scan_jobs(id) ON DELETE SET NULL,
    INDEX idx_scan_job_id (scan_job_id),
    INDEX idx_archivo_nombre (archivo_nombre(255)),
    INDEX idx_tipo_entidad (tipo_entidad),
    INDEX idx_is_sensitive (is_sensitive),
    INDEX idx_is_resolved (is_resolved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table scan_configs
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS scan_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scan_paths TEXT NOT NULL,
    extensions TEXT NOT NULL,
    entities TEXT NOT NULL,
    max_workers INT NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    schedule_type VARCHAR(50) NOT NULL DEFAULT 'none',
    schedule_time VARCHAR(10) NOT NULL DEFAULT '00:00',
    schedule_day INT NOT NULL DEFAULT 0,
    last_scheduled_run DATETIME NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table db_configs
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS db_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(191) NOT NULL UNIQUE,
    db_type VARCHAR(50) NOT NULL,
    connection_string TEXT NOT NULL,
    tables_to_scan TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
