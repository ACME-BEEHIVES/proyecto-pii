export interface ScanJob {
  id: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  root_path: string;
  started_at: string | null;
  completed_at: string | null;
  files_total: number;
  files_scanned: number;
  files_skipped: number;
  findings_count: number;
  error_message: string | null;
}

export interface ScanConfig {
  scan_paths: string[];
  extensions: string[];
  entities: string[];
  max_workers: number;
  is_active: boolean;
  schedule_type: 'none' | 'hourly' | 'daily' | 'weekly';
  schedule_time: string;
  schedule_day: number;
  db_host?: string;
  db_port?: string;
  db_user?: string;
  db_password?: string;
  db_name?: string;
  upshield_api_url?: string;
  upshield_api_key?: string;
  upshield_tenant_id?: string;
  upshield_sync_interval?: number;
  alert_emails_enabled?: boolean;
  alert_check_interval?: number;
  smtp_host?: string;
  smtp_port?: number;
  smtp_username?: string;
  smtp_password?: string;
  smtp_from?: string;
  smtp_to?: string;
}

export interface ScanFinding {
  id: number;
  scan_job_id: number;
  file_path: string;
  file_name: string;
  entity_type: string;
  detected_text: string;
  confidence_score: number;
  is_sensitive: boolean;
  is_resolved: boolean;
  resolved_at: string | null;
  resolved_by: string | null;
  resolution_method: string | null;
  resolution_notes: string | null;
  created_at: string;
}

export interface ServiceHealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  message: string | null;
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | 'error';
  service: string;
  version: string;
  environment: string;
  services: {
    database: ServiceHealthStatus;
    tika: ServiceHealthStatus;
    presidio: ServiceHealthStatus;
    watcher: ServiceHealthStatus;
  };
}

export interface FindingsStats {
  total_findings: number;
  active_findings: number;
  resolved_findings: number;
  files_scanned: number;
  scanned_files_count: number;
  scanned_db_cells_count: number;
  active_db_configs_count: number;
  findings_in_files_count: number;
  findings_in_db_count: number;
  by_type: Record<string, number>;
  by_severity: {
    ALTO: number;
    MODERADO: number;
    LIMPIO: number;
  };
  by_folder: Record<string, number>;
  global_risk_level: 'ALTO' | 'MODERADO' | 'LIMPIO';
}

export interface DsarItem {
  categoria_legal: string;
  dato_encontrado: string;
  estado_almacenamiento: string;
}

export interface DsarResponse {
  rut_consultado: string;
  resumen: {
    archivos_involucrados: number;
    alertas_datos_sensibles: number;
    nivel_riesgo_ley21719: 'ALTO' | 'MODERADO' | 'LIMPIO';
  };
  mapa_de_datos: Record<string, DsarItem[]>;
}

export interface RedactionPreviewResponse {
  file_path: string;
  findings_count: number;
  texts_to_redact: string[];
}

export interface BrowseDirResponse {
  current_path: string;
  parent_path: string | null;
  directories: string[];
}

export interface DbConfig {
  id: number;
  name: string;
  db_type: 'mysql' | 'postgresql' | 'mssql';
  tables_to_scan: Record<string, string[]>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DbConfigCreate {
  name: string;
  db_type: 'mysql' | 'postgresql' | 'mssql';
  connection_string: string;
  tables_to_scan: Record<string, string[]>;
  is_active: boolean;
}export interface IdentitySubject {
  rut: string;
  names: string[];
  emails: string[];
  phones: string[];
  birth_dates: string[];
  files: string[];
  file_paths: string[];
  risk_level: 'ALTO' | 'MODERADO' | 'LIMPIO';
  findings_count: number;
}
