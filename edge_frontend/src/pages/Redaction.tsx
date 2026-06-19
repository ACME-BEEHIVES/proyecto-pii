import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Grid from '@mui/material/Grid';
import Alert from '@mui/material/Alert';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import Divider from '@mui/material/Divider';
import Chip from '@mui/material/Chip';
import Tooltip from '@mui/material/Tooltip';
import InputAdornment from '@mui/material/InputAdornment';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogActions from '@mui/material/DialogActions';

// Icons
import SecurityIcon from '@mui/icons-material/Security';

import DownloadIcon from '@mui/icons-material/Download';
import HistoryIcon from '@mui/icons-material/History';
import SearchIcon from '@mui/icons-material/Search';
import DescriptionIcon from '@mui/icons-material/Description';
import DeleteIcon from '@mui/icons-material/Delete';
import WarningIcon from '@mui/icons-material/Warning';


import { api } from '../services/api';
import type { RedactionPreviewResponse } from '../types';

interface FileSearchResult {
  file_path: string;
  file_name: string;
  matched_findings: number;
  total_findings_in_file: number;
  entity_types: string[];
  sample_texts: string[];
}

const RedactionPage: React.FC = () => {
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<FileSearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  // Selected file state
  const [selectedFile, setSelectedFile] = useState<FileSearchResult | null>(null);

  // Preview state
  const [previewLoading, setPreviewLoading] = useState(false);
  const [preview, setPreview] = useState<RedactionPreviewResponse | null>(null);

  // Redaction state
  const [redactLoading, setRedactLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [history, setHistory] = useState<string[]>([]);
  const [successRedacted, setSuccessRedacted] = useState<string | null>(null);

  // Confirmation dialog states
  const [inPlaceConfirmOpen, setInPlaceConfirmOpen] = useState(false);
  const [quarantineConfirmOpen, setQuarantineConfirmOpen] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim().length < 2) {
      setErrorMsg('Ingresa al menos 2 caracteres para buscar.');
      return;
    }
    setErrorMsg(null);
    setSearchLoading(true);
    setHasSearched(true);
    setSelectedFile(null);
    setPreview(null);
    setSuccessRedacted(null);
    try {
      const data = await api.searchFilesForRedaction(searchQuery.trim());
      setSearchResults(data.files);
    } catch (e: any) {
      console.error('Error searching files', e);
      setErrorMsg(e.response?.data?.detail || 'Error al buscar archivos.');
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleSelectFile = async (file: FileSearchResult) => {
    setSelectedFile(file);
    setPreview(null);
    setPreviewLoading(true);
    setErrorMsg(null);
    setSuccessRedacted(null);
    try {
      const data = await api.getRedactionPreview(file.file_path);
      setPreview(data);
    } catch (e: any) {
      console.error('Error fetching redaction preview', e);
      setErrorMsg(e.response?.data?.detail || 'Error al obtener la vista previa.');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleGenerateRedacted = async () => {
    if (!selectedFile) return;
    setErrorMsg(null);
    setRedactLoading(true);
    setSuccessRedacted(null);
    try {
      const blob = await api.downloadRedactedFile(selectedFile.file_path);

      // Determine file name
      const fileName = selectedFile.file_name;
      const parts = fileName.split('.');
      const ext = parts.pop();
      const baseName = parts.join('.');
      const downloadName = `${baseName}_censurado.${ext}`;

      // Trigger browser download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', downloadName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setSuccessRedacted(`¡Censura exitosa! Archivo descargado como ${downloadName}`);
      setHistory(prev => [selectedFile.file_name, ...prev]);
    } catch (e: any) {
      console.error('Error downloading redacted file', e);
      setErrorMsg('Error al generar la copia censurada.');
    } finally {
      setRedactLoading(false);
    }
  };

  const handleInPlaceRedact = async () => {
    if (!selectedFile) return;
    setInPlaceConfirmOpen(false);
    setErrorMsg(null);
    setRedactLoading(true);
    setSuccessRedacted(null);
    try {
      const res = await api.redactInPlace(selectedFile.file_path);
      if (res.status === 'ok') {
        setSuccessRedacted(`¡Censura in-situ completada con éxito! El archivo original ha sido sobrescrito y los hallazgos asociados se han marcado como resueltos.`);
        setHistory(prev => [`[In-Situ] ${selectedFile.file_name}`, ...prev]);
        
        // Refrescar la búsqueda si hay un query activo
        if (searchQuery.trim()) {
          const data = await api.searchFilesForRedaction(searchQuery.trim());
          setSearchResults(data.files);
        }
        setSelectedFile(null);
        setPreview(null);
      } else {
        setErrorMsg(res.message || 'Error al censurar in-situ.');
      }
    } catch (e: any) {
      console.error('Error during in-place redaction', e);
      setErrorMsg(e.response?.data?.detail || 'Error al censurar in-situ el archivo.');
    } finally {
      setRedactLoading(false);
    }
  };

  const handleQuarantine = async () => {
    if (!selectedFile) return;
    setQuarantineConfirmOpen(false);
    setErrorMsg(null);
    setRedactLoading(true);
    setSuccessRedacted(null);
    try {
      const res = await api.quarantineFile(selectedFile.file_path);
      if (res.status === 'ok') {
        setSuccessRedacted(`¡Archivo movido a cuarentena! El archivo original se trasladó y se dejó un placeholder en la ruta original.`);
        setHistory(prev => [`[Cuarentena] ${selectedFile.file_name}`, ...prev]);
        
        // Refrescar la búsqueda si hay un query activo
        if (searchQuery.trim()) {
          const data = await api.searchFilesForRedaction(searchQuery.trim());
          setSearchResults(data.files);
        }
        setSelectedFile(null);
        setPreview(null);
      } else {
        setErrorMsg(res.message || 'Error al mover a cuarentena.');
      }
    } catch (e: any) {
      console.error('Error during quarantine', e);
      setErrorMsg(e.response?.data?.detail || 'Error al mover a cuarentena el archivo.');
    } finally {
      setRedactLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
          Motor de Censura de Documentos
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Busca un titular por RUT, nombre o correo y selecciona el archivo a censurar.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Left Side: Search + Results */}
        <Grid size={{ xs: 12, md: 5 }}>
          {/* Search Card */}
          <Card sx={{ border: '1px solid #E9ECEF', boxShadow: 'none', mb: 2 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                <SearchIcon color="primary" /> Buscar Titular
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                Ingresa el RUT (con o sin puntos), nombre o correo electrónico del titular.
              </Typography>

              <Box component="form" onSubmit={handleSearch}>
                <TextField
                  id="redaction-search"
                  fullWidth
                  size="small"
                  placeholder="Ej: 8.565.137-4, Pablo Ortiz, correo@ejemplo.com"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  slotProps={{
                    input: {
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon color="action" sx={{ fontSize: 20 }} />
                        </InputAdornment>
                      ),
                    },
                  }}
                  sx={{
                    mb: 1.5,
                    '& .MuiOutlinedInput-root': { borderRadius: 2, bgcolor: '#FAFBFD' },
                  }}
                />

                {errorMsg && (
                  <Alert severity="error" sx={{ mb: 1.5, '& .MuiAlert-message': { fontSize: '0.8rem' } }}>
                    {errorMsg}
                  </Alert>
                )}

                <Button
                  variant="contained"
                  color="primary"
                  fullWidth
                  type="submit"
                  disabled={searchLoading}
                  startIcon={searchLoading ? <CircularProgress size={20} /> : <SearchIcon />}
                >
                  {searchLoading ? 'Buscando...' : 'Buscar Archivos'}
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Search Results */}
          {hasSearched && (
            <Card sx={{ border: '1px solid #E9ECEF', boxShadow: 'none', mb: 2 }}>
              <CardContent sx={{ p: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <DescriptionIcon color="action" sx={{ fontSize: 18 }} />
                  {searchResults.length > 0 ? `${searchResults.length} archivos encontrados` : 'Sin resultados'}
                </Typography>

                {searchResults.length > 0 ? (
                  <List sx={{ p: 0, maxHeight: 320, overflowY: 'auto' }}>
                    {searchResults.map((file, idx) => (
                      <ListItemButton
                        key={idx}
                        selected={selectedFile?.file_path === file.file_path}
                        onClick={() => handleSelectFile(file)}
                        sx={{
                          borderRadius: 1.5,
                          mb: 0.5,
                          border: '1px solid',
                          borderColor: selectedFile?.file_path === file.file_path ? 'primary.main' : '#E9ECEF',
                          bgcolor: selectedFile?.file_path === file.file_path ? 'rgba(0, 123, 255, 0.04)' : 'transparent',
                          '&:hover': { bgcolor: 'rgba(0, 123, 255, 0.06)' },
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <DescriptionIcon color={selectedFile?.file_path === file.file_path ? 'primary' : 'action'} sx={{ fontSize: 20 }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography variant="body2" sx={{ fontWeight: 600, wordBreak: 'break-all' }}>
                              {file.file_name}
                            </Typography>
                          }
                          secondary={
                            <Box>
                              <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                {file.matched_findings} coincidencias · {file.total_findings_in_file} hallazgos PII totales
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                                {file.entity_types.slice(0, 4).map((et, i) => (
                                  <Chip key={i} label={et} size="small" sx={{ height: 18, fontSize: '0.65rem' }} />
                                ))}
                              </Box>
                            </Box>
                          }
                        />
                      </ListItemButton>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                    No se encontraron archivos con datos que coincidan con "{searchQuery}".
                  </Typography>
                )}
              </CardContent>
            </Card>
          )}

          {/* Censorship History */}
          <Card sx={{ border: '1px solid #E9ECEF', boxShadow: 'none' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                <HistoryIcon color="action" /> Historial de Censuras
              </Typography>
              <List sx={{ mt: 1, p: 0 }}>
                {history.length > 0 ? (
                  history.map((name, idx) => (
                    <ListItem key={idx} sx={{ borderBottom: idx < history.length - 1 ? '1px solid #E9ECEF' : 'none', px: 1, py: 1 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <CheckCircleIcon color="success" sx={{ fontSize: 18 }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={name}
                        sx={{ '& .MuiListItemText-primary': { fontSize: '0.85rem', fontWeight: 600 } }}
                      />
                    </ListItem>
                  ))
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 1, textAlign: 'center' }}>
                    No hay archivos censurados en esta sesión.
                  </Typography>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Side: Preview & Download */}
        <Grid size={{ xs: 12, md: 7 }}>
          {previewLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : selectedFile && preview ? (
            <Box>
              {successRedacted && (
                <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mb: 3 }}>
                  {successRedacted}
                </Alert>
              )}

              <Card sx={{ border: '1px solid #E9ECEF', boxShadow: 'none' }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 700 }} gutterBottom>
                    Vista Previa de Sanitización
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                    Se aplicará una máscara permanente sobre los siguientes términos y regiones.
                  </Typography>

                  <Box sx={{ p: 2, bgcolor: '#F8F9FA', borderRadius: 1, mb: 3, border: '1px solid #E9ECEF' }}>
                    <Typography variant="body2" color="text.secondary">ARCHIVO SELECCIONADO</Typography>
                    <Typography variant="body1" sx={{ fontWeight: 700, wordBreak: 'break-all', mt: 0.5 }}>
                      {selectedFile.file_name}
                    </Typography>
                    <Tooltip title={selectedFile.file_path} arrow>
                      <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace', display: 'block', mt: 0.5, cursor: 'help', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {selectedFile.file_path}
                      </Typography>
                    </Tooltip>
                  </Box>

                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid size={12}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }} gutterBottom>
                        Hallazgos PII a Censurar ({preview.findings_count})
                      </Typography>
                      <Divider />

                      {preview.texts_to_redact.length > 0 ? (
                        <List sx={{ mt: 1, maxHeight: 260, overflowY: 'auto' }}>
                          {preview.texts_to_redact.map((text, idx) => (
                            <ListItem key={idx} sx={{ py: 0.5, px: 0 }}>
                              <ListItemText
                                primary={
                                  <Box component="span" sx={{ textDecoration: 'line-through', color: 'error.main', fontWeight: 600 }}>
                                    {text}
                                  </Box>
                                }
                                secondary="Será reemplazado por máscara negra o [REDACTADO]"
                                sx={{
                                  '& .MuiListItemText-primary': { fontSize: '0.9rem' },
                                  '& .MuiListItemText-secondary': { fontSize: '0.75rem' }
                                }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      ) : (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
                          No se encontraron datos que requieran censura en este archivo.
                        </Typography>
                      )}
                    </Grid>
                  </Grid>

                  <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                    <Button
                      variant="contained"
                      color="success"
                      fullWidth
                      disabled={redactLoading}
                      startIcon={redactLoading ? <CircularProgress size={20} /> : <DownloadIcon />}
                      onClick={handleGenerateRedacted}
                    >
                      {redactLoading ? 'Generando...' : 'Descargar Copia Censurada'}
                    </Button>
                    
                    <Grid container spacing={1.5}>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Button
                          variant="outlined"
                          color="warning"
                          fullWidth
                          disabled={redactLoading}
                          startIcon={redactLoading ? <CircularProgress size={20} /> : <SecurityIcon />}
                          onClick={() => setInPlaceConfirmOpen(true)}
                        >
                          Censurar In-Situ
                        </Button>
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Button
                          variant="outlined"
                          color="error"
                          fullWidth
                          disabled={redactLoading}
                          startIcon={redactLoading ? <CircularProgress size={20} /> : <DeleteIcon />}
                          onClick={() => setQuarantineConfirmOpen(true)}
                        >
                          Mover a Cuarentena
                        </Button>
                      </Grid>
                    </Grid>
                  </Box>
                </CardContent>
              </Card>
            </Box>
          ) : selectedFile ? (
            <Alert severity="warning">
              No se pudo cargar la vista previa del archivo. Asegúrese de que el archivo exista y esté accesible.
            </Alert>
          ) : (
            <Paper variant="outlined" sx={{ py: 8, textAlign: 'center', border: '1px dashed #E9ECEF' }}>
              <SecurityIcon sx={{ fontSize: 48, color: 'text.secondary', opacity: 0.5, mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                {hasSearched
                  ? 'Selecciona un archivo de la lista de resultados para ver qué datos se censurarán.'
                  : 'Busca un titular por RUT, nombre o correo para encontrar los archivos que contienen sus datos personales.'}
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>

      {/* Diálogo de Confirmación para Censura In-Situ */}
      <Dialog
        open={inPlaceConfirmOpen}
        onClose={() => setInPlaceConfirmOpen(false)}
        aria-labelledby="inplace-confirm-title"
        aria-describedby="inplace-confirm-description"
      >
        <DialogTitle id="inplace-confirm-title" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 700 }}>
          <WarningIcon color="warning" /> ¿Confirmar Censura In-Situ?
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="inplace-confirm-description" variant="body2">
            Esta acción es <strong>destructiva</strong> y no se puede deshacer. Se reemplazará el contenido sensible directamente en el archivo original (<strong>{selectedFile?.file_name}</strong>) con máscaras o marcas [REDACTADO].
          </DialogContentText>
          <DialogContentText sx={{ mt: 1.5 }} variant="body2">
            Todos los hallazgos asociados en este archivo se marcarán como <strong>resueltos</strong> en el sistema.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setInPlaceConfirmOpen(false)} color="secondary" variant="outlined" size="small">
            Cancelar
          </Button>
          <Button onClick={handleInPlaceRedact} color="warning" variant="contained" size="small" autoFocus>
            Censurar y Sobrescribir
          </Button>
        </DialogActions>
      </Dialog>

      {/* Diálogo de Confirmación para Cuarentena */}
      <Dialog
        open={quarantineConfirmOpen}
        onClose={() => setQuarantineConfirmOpen(false)}
        aria-labelledby="quarantine-confirm-title"
        aria-describedby="quarantine-confirm-description"
      >
        <DialogTitle id="quarantine-confirm-title" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 700 }}>
          <WarningIcon color="error" /> ¿Confirmar Envío a Cuarentena?
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="quarantine-confirm-description" variant="body2">
            El archivo original (<strong>{selectedFile?.file_name}</strong>) será movido de forma permanente a la carpeta segura de cuarentena del agente. En su lugar de origen, se creará un archivo de texto con la extensión <code>.quarantine.txt</code> informando de la acción.
          </DialogContentText>
          <DialogContentText sx={{ mt: 1.5 }} variant="body2">
            Todos los hallazgos del archivo se marcarán como <strong>resueltos</strong> y su ruta en la base de datos se actualizará a la ubicación en cuarentena.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setQuarantineConfirmOpen(false)} color="secondary" variant="outlined" size="small">
            Cancelar
          </Button>
          <Button onClick={handleQuarantine} color="error" variant="contained" size="small" autoFocus>
            Mover a Cuarentena
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RedactionPage;
