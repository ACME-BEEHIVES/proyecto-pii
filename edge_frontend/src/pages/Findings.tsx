import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import Drawer from '@mui/material/Drawer';
import Divider from '@mui/material/Divider';
import CircularProgress from '@mui/material/CircularProgress';
import Grid from '@mui/material/Grid';
import Alert from '@mui/material/Alert';
import IconButton from '@mui/material/IconButton';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Select from '@mui/material/Select';
import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';
import Chip from '@mui/material/Chip';
import { DataGrid } from '@mui/x-data-grid';
import type { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';

// Icons
import DownloadIcon from '@mui/icons-material/Download';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import CloseIcon from '@mui/icons-material/Close';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import StorageIcon from '@mui/icons-material/Storage';
import DescriptionIcon from '@mui/icons-material/Description';

import { api } from '../services/api';
import type { ScanFinding } from '../types';
import PiiRiskBadge from '../components/PiiRiskBadge';
import PiiEntityIcon from '../components/PiiEntityIcon';

const FindingsPage: React.FC = () => {
  const [findings, setFindings] = useState<ScanFinding[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [entityFilter, setEntityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // active, resolved, all
  const [riskFilter, setRiskFilter] = useState('all'); // all, alto, moderado

  // Detail Drawer
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detailFinding, setDetailFinding] = useState<ScanFinding | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [showSensitiveText, setShowSensitiveText] = useState(false);

  // Resolve Dialog
  const [resolveDialogOpen, setResolveDialogOpen] = useState(false);
  const [resolveTargetId, setResolveTargetId] = useState<number | null>(null);
  const [resolveBy, setResolveBy] = useState('');
  const [resolveMethod, setResolveMethod] = useState('');
  const [resolveNotes, setResolveNotes] = useState('');

  // Pagination
  const [pageSize, setPageSize] = useState(50);

  const fetchFindings = async () => {
    try {
      setLoading(true);
      const isResolvedParam = statusFilter === 'all' ? undefined : statusFilter === 'resolved';
      const isSensitiveParam = riskFilter === 'all' ? undefined : riskFilter === 'alto';
      const data = await api.getFindings({
        entity_type: entityFilter || undefined,
        file_path: searchTerm || undefined,
        is_resolved: isResolvedParam,
        is_sensitive: isSensitiveParam,
        limit: 10000, // Load a good bulk of data for easy Grid usage
      });
      setFindings(data);
    } catch (e) {
      console.error('Error fetching findings', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFindings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [entityFilter, statusFilter, riskFilter]);

  // Handle manual trigger for search button or enter
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchFindings();
  };

  // Open detail panel
  const handleRowClick = async (id: number) => {
    setSelectedId(id);
    setDetailFinding(null);
    setShowSensitiveText(false);
    try {
      setDetailLoading(true);
      const details = await api.getFindingDetails(id);
      setDetailFinding(details);
    } catch (e) {
      console.error('Error getting details', e);
    } finally {
      setDetailLoading(false);
    }
  };

  const openResolveDialog = (id: number) => {
    setResolveTargetId(id);
    setResolveBy('');
    setResolveMethod('');
    setResolveNotes('');
    setResolveDialogOpen(true);
  };

  const handleResolveConfirm = async () => {
    if (!resolveTargetId || !resolveBy || !resolveMethod) return;
    try {
      await api.resolveFinding(resolveTargetId, {
        resolved_by: resolveBy,
        resolution_method: resolveMethod,
        resolution_notes: resolveNotes,
      });
      fetchFindings();
      if (detailFinding && detailFinding.id === resolveTargetId) {
        setDetailFinding({
          ...detailFinding,
          is_resolved: true,
          resolved_at: new Date().toISOString(),
          resolved_by: resolveBy,
          resolution_method: resolveMethod,
          resolution_notes: resolveNotes,
        });
      }
      setResolveDialogOpen(false);
    } catch (e) {
      console.error('Error resolving finding', e);
    }
  };

  const RESOLUTION_METHODS: { value: string; label: string }[] = [
    { value: 'manual_review', label: 'Revisión manual — No requiere acción' },
    { value: 'data_deleted', label: 'Dato eliminado de la fuente' },
    { value: 'data_anonymized', label: 'Dato anonimizado / seudonimizado' },
    { value: 'consent_obtained', label: 'Consentimiento del titular obtenido' },
    { value: 'legal_basis', label: 'Base legal vigente (contrato, ley, etc.)' },
    { value: 'redacted_copy', label: 'Archivo censurado (copia generada)' },
    { value: 'redacted_in_place', label: 'Archivo censurado en origen' },
    { value: 'quarantined', label: 'Archivo movido a cuarentena' },
    { value: 'other', label: 'Otro (ver notas)' },
  ];

  const handleRedactInPlace = async (filePath: string) => {
    if (!confirm('¿Está seguro de censurar y sobreescribir el archivo original? Esta acción modificará el archivo permanentemente.')) return;
    try {
      setDetailLoading(true);
      await api.redactInPlace(filePath);
      alert('Archivo censurado in-situ exitosamente.');
      fetchFindings();
      if (selectedId) handleRowClick(selectedId);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Error al censurar archivo.');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleQuarantine = async (filePath: string) => {
    if (!confirm('¿Está seguro de mover este archivo a la carpeta de cuarentena? El archivo original será reemplazado por una nota explicativa.')) return;
    try {
      setDetailLoading(true);
      await api.quarantineFile(filePath);
      alert(`Archivo movido exitosamente a cuarentena.`);
      fetchFindings();
      if (selectedId) handleRowClick(selectedId);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Error al mover el archivo a cuarentena.');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleExport = () => {
    window.open(api.exportFindingsUrl(), '_blank');
  };

  const entityTypes = [
    { value: 'CHILE_RUT', label: 'RUT' },
    { value: 'EMAIL_ADDRESS', label: 'Email' },
    { value: 'PERSON', label: 'Persona' },
    { value: 'PHONE_NUMBER', label: 'Teléfono' },
    { value: 'DATE_TIME', label: 'Fecha' },
    { value: 'DOMICILIO', label: 'Domicilio' },
    { value: 'NACIONALIDAD', label: 'Nacionalidad' },
    { value: 'PASAPORTE', label: 'Pasaporte' },
    { value: 'LICENCIA_CONDUCIR', label: 'Licencia Conducir' },
    { value: 'CUENTA_BANCARIA', label: 'Cuenta Bancaria' },
    { value: 'NUMERO_SERIE_DOC', label: 'N° Serie Doc.' },
    { value: 'DATA_SALUD', label: 'Salud' },
    { value: 'DATA_ETNIA', label: 'Etnia' },
    { value: 'DATA_POLITICA', label: 'Política' },
    { value: 'DATA_RELIGION', label: 'Religión' },
    { value: 'DATA_SEXUALIDAD', label: 'Sexualidad' },
    { value: 'DATA_SINDICAL', label: 'Sindical' },
    { value: 'DATA_SOCIOECONOMICO', label: 'Socioeconómico' },
    { value: 'DATA_IDEOLOGIA', label: 'Ideología' },
    { value: 'DATA_BIOLOGICO', label: 'Biológico' },
    { value: 'DATA_BIOMETRICO', label: 'Biométrico' },
    { value: 'DATA_PENAL', label: 'Penal' },
  ];

  const columns: GridColDef[] = [
    {
      field: 'file_name',
      headerName: 'Origen / Archivo',
      flex: 1,
      minWidth: 180,
      renderCell: (params: GridRenderCellParams<ScanFinding, string>) => {
        const isDb = params.row.file_path.startsWith('db://');
        return (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
            {isDb ? (
              <StorageIcon color="primary" sx={{ fontSize: 16 }} />
            ) : (
              <DescriptionIcon color="action" sx={{ fontSize: 16 }} />
            )}
            <TooltipTitle text={params.value || ''} />
          </Box>
        );
      },
    },
    {
      field: 'entity_type',
      headerName: 'Tipo de Entidad',
      width: 160,
      renderCell: (params: GridRenderCellParams<ScanFinding, string>) => (
        <PiiEntityIcon entityType={params.value || ''} showLabel size="small" />
      ),
    },
    {
      field: 'detected_text',
      headerName: 'Dato Detectado',
      flex: 1.2,
      minWidth: 180,
      renderCell: (params: GridRenderCellParams<ScanFinding, string>) => {
        const isSensitive = params.row.is_sensitive;
        if (isSensitive) {
          return (
            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', display: 'flex', alignItems: 'center', gap: 0.5 }}>
              🔒 [Cifrado en base de datos]
            </Typography>
          );
        }
        return params.value;
      },
    },
    {
      field: 'confidence_score',
      headerName: 'Certeza',
      width: 100,
      renderCell: (params: GridRenderCellParams<ScanFinding, number>) => (
        <span>{Math.round((params.value || 0) * 100)}%</span>
      ),
    },
    {
      field: 'is_sensitive',
      headerName: 'Nivel Riesgo',
      width: 120,
      renderCell: (params: GridRenderCellParams<ScanFinding, boolean>) => (
        <PiiRiskBadge level={params.value ? 'ALTO' : 'MODERADO'} />
      ),
    },
    {
      field: 'is_resolved',
      headerName: 'Estado',
      width: 120,
      renderCell: (params: GridRenderCellParams<ScanFinding, boolean>) => (
        <Typography
          variant="body2"
          sx={{ fontWeight: 600 }}
          color={params.value ? 'success.main' : 'error.main'}
        >
          {params.value ? 'Mitigado' : 'Pendiente'}
        </Typography>
      ),
    },
    {
      field: 'actions',
      headerName: 'Acción',
      width: 100,
      sortable: false,
      renderCell: (params: GridRenderCellParams<ScanFinding>) => (
        <Button
          size="small"
          variant="outlined"
          onClick={() => handleRowClick(params.row.id)}
          endIcon={<OpenInNewIcon sx={{ fontSize: 12 }} />}
        >
          Detalle
        </Button>
      ),
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
            Hallazgos de Seguridad
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Lista completa de datos personales identificados en la red local del cliente
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<DownloadIcon />} onClick={handleExport}>
          Exportar CSV
        </Button>
      </Box>

      {/* Filter toolbar */}
      <Card sx={{ mb: 3, boxShadow: 'none', border: '1px solid #E9ECEF' }}>
        <CardContent sx={{ p: 2.5 }}>
          <Box component="form" onSubmit={handleSearchSubmit} sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            <TextField
              label="Buscar por ruta, archivo o dato (no cifrado)"
              variant="outlined"
              size="small"
              sx={{ flexGrow: 1, minWidth: 200 }}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            
            <TextField
              select
              label="Categoría Legal"
              variant="outlined"
              size="small"
              sx={{ width: 180 }}
              value={entityFilter}
              onChange={(e) => setEntityFilter(e.target.value)}
            >
              <MenuItem value="">Todas</MenuItem>
              {entityTypes.map((t) => (
                <MenuItem key={t.value} value={t.value}>
                  {t.label}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              select
              label="Estado"
              variant="outlined"
              size="small"
              sx={{ width: 150 }}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="all">Todos</MenuItem>
              <MenuItem value="active">Pendientes</MenuItem>
              <MenuItem value="resolved">Mitigados</MenuItem>
            </TextField>

            <TextField
              select
              label="Nivel Riesgo"
              variant="outlined"
              size="small"
              sx={{ width: 150 }}
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
            >
              <MenuItem value="all">Todos</MenuItem>
              <MenuItem value="alto">Alto</MenuItem>
              <MenuItem value="moderado">Moderado</MenuItem>
            </TextField>

            <Button variant="contained" type="submit">
              Buscar
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Data Grid container */}
      <Card sx={{ border: '1px solid #E9ECEF', boxShadow: 'none' }}>
        <Box sx={{ height: 600, width: '100%' }}>
          <DataGrid
            rows={findings}
            columns={columns}
            loading={loading}
            initialState={{
              pagination: { paginationModel: { pageSize } },
            }}
            pageSizeOptions={[25, 50, 100]}
            onPaginationModelChange={(model) => setPageSize(model.pageSize)}
            disableRowSelectionOnClick
            sx={{
              border: 'none',
              '& .MuiDataGrid-columnHeaders': {
                backgroundColor: '#F8F9FA',
                fontWeight: 600,
                borderBottom: '1px solid #E9ECEF',
              },
              '& .MuiDataGrid-row:hover': {
                backgroundColor: 'rgba(0, 123, 255, 0.03)',
              },
              '& .MuiDataGrid-cell': {
                borderBottom: '1px solid #E9ECEF',
              },
            }}
          />
        </Box>
      </Card>

      {/* Details drawer */}
      <Drawer
        anchor="right"
        open={selectedId !== null}
        onClose={() => setSelectedId(null)}
        sx={{
          '& .MuiDrawer-paper': {
            width: { xs: '100%', sm: 480 },
            p: 3,
            backgroundColor: '#FFFFFF',
            color: '#343A40',
            boxSizing: 'border-box',
          },
        }}
      >
        {selectedId && (
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Detalle del Hallazgo
              </Typography>
              <IconButton onClick={() => setSelectedId(null)}>
                <CloseIcon />
              </IconButton>
            </Box>
            <Divider sx={{ mb: 3 }} />

            {detailLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                <CircularProgress />
              </Box>
            ) : detailFinding ? (
              <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
                <Grid container spacing={2.5}>
                  <Grid size={12}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>ARCHIVO</Typography>
                    <Typography variant="body1" sx={{ fontWeight: 600, wordBreak: 'break-all' }}>
                      {detailFinding.file_name}
                    </Typography>
                  </Grid>

                  <Grid size={12}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>RUTA COMPLETA</Typography>
                    <Typography variant="body2" sx={{ wordBreak: 'break-all', fontFamily: 'monospace', bg: '#F8F9FA', p: 1, borderRadius: 1 }}>
                      {detailFinding.file_path}
                    </Typography>
                  </Grid>

                  <Grid size={6}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>TIPO DE ENTIDAD</Typography>
                    <Box sx={{ mt: 0.5 }}>
                      <PiiEntityIcon entityType={detailFinding.entity_type} showLabel />
                    </Box>
                  </Grid>

                  <Grid size={6}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>NIVEL RIESGO LEY 21.719</Typography>
                    <Box sx={{ mt: 0.5 }}>
                      <PiiRiskBadge level={detailFinding.is_sensitive ? 'ALTO' : 'MODERADO'} size="medium" />
                    </Box>
                  </Grid>

                  <Grid size={12}>
                    <Box sx={{ border: '1px solid #E9ECEF', borderRadius: 1, p: 2, bg: '#F8F9FA' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          {detailFinding.is_sensitive ? "DATO DETECTADO (CIFRADO)" : "DATO DETECTADO (ENMASCARADO)"}
                        </Typography>
                        {detailFinding.is_sensitive && (
                          <Button
                            size="small"
                            variant="text"
                            onClick={() => setShowSensitiveText(!showSensitiveText)}
                            startIcon={showSensitiveText ? <VisibilityOffIcon /> : <VisibilityIcon />}
                          >
                            {showSensitiveText ? 'Ocultar' : 'Ver Descifrado'}
                          </Button>
                        )}
                      </Box>
                      
                      {!detailFinding.is_sensitive || showSensitiveText ? (
                        <Typography variant="body1" sx={{ fontWeight: 700, wordBreak: 'break-all', color: 'error.main' }}>
                          {detailFinding.detected_text}
                        </Typography>
                      ) : (
                        <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                          🔒 Haz clic en "Ver Descifrado" para desencriptar el valor confidencial
                        </Typography>
                      )}
                    </Box>
                  </Grid>

                  <Grid size={12}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>CERTEZA DETECCIÓN</Typography>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {Math.round(detailFinding.confidence_score * 100)}%
                    </Typography>
                  </Grid>

                  <Grid size={12}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>ESTADO MITIGACIÓN</Typography>
                    {detailFinding.is_resolved ? (
                      <Box>
                        <Alert severity="success" sx={{ mb: 1.5 }}>
                          Mitigado el {detailFinding.resolved_at ? new Date(detailFinding.resolved_at).toLocaleString() : ''}
                        </Alert>
                        {detailFinding.resolved_by && (
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>RESUELTO POR</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>{detailFinding.resolved_by}</Typography>
                          </Box>
                        )}
                        {detailFinding.resolution_method && (
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>MÉTODO DE MITIGACIÓN</Typography>
                            <Chip
                              label={RESOLUTION_METHODS.find(m => m.value === detailFinding.resolution_method)?.label || detailFinding.resolution_method}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          </Box>
                        )}
                        {detailFinding.resolution_notes && (
                          <Box>
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>NOTAS / JUSTIFICACIÓN</Typography>
                            <Typography variant="body2" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
                              {detailFinding.resolution_notes}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    ) : (
                      <Box sx={{ mt: 1, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                        <Button
                          variant="contained"
                          color="success"
                          fullWidth
                          startIcon={<CheckCircleIcon />}
                          onClick={() => openResolveDialog(detailFinding.id)}
                        >
                          Marcar como Mitigado / Resuelto
                        </Button>

                        {!detailFinding.file_path.startsWith('db://') && (
                          <>
                            <Button
                              variant="outlined"
                              color="primary"
                              fullWidth
                              onClick={() => handleRedactInPlace(detailFinding.file_path)}
                            >
                              Censurar en Origen (Sobreescribir)
                            </Button>

                            <Button
                              variant="outlined"
                              color="warning"
                              fullWidth
                              onClick={() => handleQuarantine(detailFinding.file_path)}
                            >
                              Mover a Cuarentena
                            </Button>
                          </>
                        )}
                      </Box>
                    )}
                  </Grid>
                </Grid>
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No se pudieron cargar los detalles del hallazgo.
              </Typography>
            )}
          </Box>
        )}
      </Drawer>

      {/* ====== RESOLVE EVIDENCE DIALOG ====== */}
      <Dialog open={resolveDialogOpen} onClose={() => setResolveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>Registrar Evidencia de Mitigación</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: '16px !important' }}>
          <TextField
            label="Nombre del operador"
            placeholder="Ej: Pablo Ortiz"
            value={resolveBy}
            onChange={(e) => setResolveBy(e.target.value)}
            required
            fullWidth
            size="small"
          />
          <FormControl fullWidth size="small" required>
            <InputLabel>Método de mitigación</InputLabel>
            <Select
              value={resolveMethod}
              label="Método de mitigación"
              onChange={(e) => setResolveMethod(e.target.value as string)}
            >
              {RESOLUTION_METHODS.map((m) => (
                <MenuItem key={m.value} value={m.value}>{m.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="Notas / Justificación (opcional)"
            placeholder="Describa la acción tomada, evidencia de respaldo, etc."
            value={resolveNotes}
            onChange={(e) => setResolveNotes(e.target.value)}
            multiline
            rows={3}
            fullWidth
            size="small"
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setResolveDialogOpen(false)} color="inherit">Cancelar</Button>
          <Button
            onClick={handleResolveConfirm}
            variant="contained"
            color="success"
            disabled={!resolveBy || !resolveMethod}
            startIcon={<CheckCircleIcon />}
          >
            Confirmar Mitigación
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Tooltip helper component for cell truncation
const TooltipTitle: React.FC<{ text: string }> = ({ text }) => {
  return (
    <Box sx={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={text}>
      {text}
    </Box>
  );
};

export default FindingsPage;
