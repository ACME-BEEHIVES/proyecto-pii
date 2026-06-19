import axios from 'axios';
import type {
  ScanJob,
  ScanConfig,
  ScanFinding,
  HealthResponse,
  FindingsStats,
  DsarResponse,
  RedactionPreviewResponse,
  BrowseDirResponse,
  DbConfig,
  DbConfigCreate,
  IdentitySubject,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // --- Scan Endpoints ---
  startScan: async (): Promise<ScanJob> => {
    const response = await apiClient.post<ScanJob>('/scan/start');
    return response.data;
  },

  stopScan: async (jobId: number): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>('/scan/stop', { job_id: jobId });
    return response.data;
  },

  getScanStatus: async (): Promise<ScanJob> => {
    const response = await apiClient.get<ScanJob>('/scan/status');
    return response.data;
  },

  getScanHistory: async (page = 1, limit = 10): Promise<ScanJob[]> => {
    const response = await apiClient.get<ScanJob[]>('/scan/history', {
      params: { page, limit },
    });
    return response.data;
  },

  // --- Findings Endpoints ---
  getFindings: async (params: {
    page?: number;
    limit?: number;
    entity_type?: string;
    file_path?: string;
    is_resolved?: boolean;
    is_sensitive?: boolean;
  }): Promise<ScanFinding[]> => {
    const response = await apiClient.get<ScanFinding[]>('/findings', { params });
    return response.data;
  },

  getFindingDetails: async (id: number): Promise<ScanFinding> => {
    const response = await apiClient.get<ScanFinding>(`/findings/${id}`);
    return response.data;
  },

  getFindingsStats: async (): Promise<FindingsStats> => {
    const response = await apiClient.get<any>('/findings/stats');
    const data = response.data;
    return {
      total_findings: data.total_findings,
      active_findings: data.active_findings,
      resolved_findings: data.resolved_findings,
      files_scanned: data.scanned_files_count,
      scanned_files_count: data.scanned_files_count || 0,
      scanned_db_cells_count: data.scanned_db_cells_count || 0,
      active_db_configs_count: data.active_db_configs_count || 0,
      findings_in_files_count: data.findings_in_files_count || 0,
      findings_in_db_count: data.findings_in_db_count || 0,
      by_type: data.findings_by_type || {},
      by_severity: data.findings_by_severity || { ALTO: 0, MODERADO: 0, LIMPIO: 0 },
      by_folder: data.findings_by_folder || {},
      global_risk_level: data.global_risk_level || 'LIMPIO',
    };
  },

  resolveFinding: async (id: number, evidence: {
    resolved_by: string;
    resolution_method: string;
    resolution_notes: string;
  }): Promise<ScanFinding> => {
    const response = await apiClient.patch<ScanFinding>(`/findings/${id}/resolve`, evidence);
    return response.data;
  },

  exportFindingsUrl: (): string => {
    return `${API_BASE_URL}/findings/export`;
  },

  // --- Config Endpoints ---
  getConfig: async (): Promise<ScanConfig> => {
    const response = await apiClient.get<ScanConfig>('/config');
    return response.data;
  },

  updateConfig: async (config: ScanConfig): Promise<ScanConfig> => {
    const response = await apiClient.put<ScanConfig>('/config', config);
    return response.data;
  },

  testPath: async (path: string): Promise<{ status: 'ok' | 'error'; message?: string }> => {
    const response = await apiClient.post<{ status: 'ok' | 'error'; message?: string }>('/config/test-path', { path });
    return response.data;
  },

  browseDir: async (path?: string): Promise<BrowseDirResponse> => {
    const response = await apiClient.get<BrowseDirResponse>('/config/browse', { params: { path } });
    return response.data;
  },

  // --- DSAR Endpoints ---
  getDsarMapping: async (rut: string): Promise<DsarResponse> => {
    const response = await apiClient.get<DsarResponse>(`/dsar/${rut}`);
    return response.data;
  },

  // --- Health Endpoints ---
  getHealth: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  // --- Redaction Endpoints ---
  searchFilesForRedaction: async (query: string): Promise<{ query: string; total_files: number; files: Array<{ file_path: string; file_name: string; matched_findings: number; total_findings_in_file: number; entity_types: string[]; sample_texts: string[] }> }> => {
    const response = await apiClient.get('/redaction/search', { params: { q: query } });
    return response.data;
  },

  getRedactionPreview: async (filePath: string): Promise<RedactionPreviewResponse> => {
    const response = await apiClient.post<RedactionPreviewResponse>('/redaction/preview', { file_path: filePath });
    return response.data;
  },

  downloadRedactedFile: async (filePath: string): Promise<Blob> => {
    const response = await apiClient.post<Blob>(
      '/redaction/generate',
      { file_path: filePath },
      { responseType: 'blob' }
    );
    return response.data;
  },

  redactInPlace: async (filePath: string): Promise<{ status: string; message: string }> => {
    const response = await apiClient.post<{ status: string; message: string }>('/redaction/in-place', { file_path: filePath });
    return response.data;
  },

  quarantineFile: async (filePath: string): Promise<{ status: string; message: string; new_path: string }> => {
    const response = await apiClient.post<{ status: string; message: string; new_path: string }>('/redaction/quarantine', { file_path: filePath });
    return response.data;
  },

  // --- DB Config Endpoints ---
  getDbConfigs: async (): Promise<DbConfig[]> => {
    const response = await apiClient.get<DbConfig[]>('/db-config');
    return response.data;
  },

  createDbConfig: async (config: DbConfigCreate): Promise<DbConfig> => {
    const response = await apiClient.post<DbConfig>('/db-config', config);
    return response.data;
  },

  updateDbConfig: async (id: number, config: Partial<DbConfigCreate>): Promise<DbConfig> => {
    const response = await apiClient.put<DbConfig>(`/db-config/${id}`, config);
    return response.data;
  },

  deleteDbConfig: async (id: number): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/db-config/${id}`);
    return response.data;
  },

  testDbConnection: async (params: {
    db_type: string;
    host?: string;
    port?: number;
    user?: string;
    password?: string;
    database?: string;
    connection_string?: string;
  }): Promise<{ status: 'ok' | 'error'; message: string; connection_string?: string }> => {
    const response = await apiClient.post<any>('/db-config/test', params);
    return response.data;
  },

  discoverDbSchema: async (params: {
    db_type: string;
    host?: string;
    port?: number;
    user?: string;
    password?: string;
    database?: string;
    connection_string?: string;
  }): Promise<{ status: 'ok' | 'error'; tables: Record<string, string[]>; connection_string: string }> => {
    const response = await apiClient.post<any>('/db-config/discover-schema', params);
    return response.data;
  },

  discoverDbSchemaExisting: async (id: number): Promise<{ status: 'ok' | 'error'; tables: Record<string, string[]> }> => {
    const response = await apiClient.post<any>(`/db-config/${id}/discover-schema`);
    return response.data;
  },

  runDbScan: async (id: number): Promise<ScanJob> => {
    const response = await apiClient.post<ScanJob>(`/db-config/${id}/scan`);
    return response.data;
  },

  // --- Identity Graph Endpoints ---
  getIdentitySubjects: async (): Promise<IdentitySubject[]> => {
    const response = await apiClient.get<IdentitySubject[]>('/identity/subjects');
    return response.data;
  },
};
