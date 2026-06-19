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
import Divider from '@mui/material/Divider';

// Icons
import SearchIcon from '@mui/icons-material/Search';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import ArticleIcon from '@mui/icons-material/Article';

import { api } from '../services/api';
import type { DsarResponse } from '../types';
import PiiRiskBadge from '../components/PiiRiskBadge';
import PiiEntityIcon from '../components/PiiEntityIcon';

const DsarLookupPage: React.FC = () => {
  const [rut, setRut] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DsarResponse | null>(null);
  const [searched, setSearched] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const cleanRut = (rawRut: string) => {
    return rawRut.replace(/[^0-9kK]/g, '');
  };

  const validateRut = (rawRut: string) => {
    const cleaned = cleanRut(rawRut);
    if (cleaned.length < 8) return false;
    // Simple format validate
    return /^\d{7,8}[0-9kK]$/.test(cleaned);
  };

  const formatRut = (rawRut: string) => {
    const cleaned = cleanRut(rawRut);
    if (cleaned.length < 2) return cleaned;
    
    const dv = cleaned.slice(-1);
    let nums = cleaned.slice(0, -1);
    
    // Add dots
    let formatted = '';
    while (nums.length > 3) {
      formatted = '.' + nums.slice(-3) + formatted;
      nums = nums.slice(0, -3);
    }
    formatted = nums + formatted + '-' + dv;
    return formatted;
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleaned = cleanRut(rut);
    if (!validateRut(cleaned)) {
      setErrorMsg('Por favor ingresa un RUT chileno válido (sin puntos y con guion, o solo números).');
      return;
    }
    setErrorMsg(null);
    setLoading(true);
    setSearched(true);
    try {
      // API call expects RUT. Let's send the cleaned or formatted RUT.
      // The backend filters by detected_text. Since motor records RUTs formatted (e.g. 19.999.999-9),
      // we format the search input before querying.
      const queryRut = formatRut(cleaned);
      const data = await api.getDsarMapping(queryRut);
      setResult(data);
    } catch (e) {
      console.error('Error fetching DSAR mapping', e);
      setErrorMsg('Error al consultar datos en el agente local');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
          Derechos ARCO / DSAR Lookup
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Cumple con la Ley 21.719 en Chile. Busca qué datos personales almacenas de un titular por su RUT y descífralos al vuelo.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Search query box */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ border: '1px solid #E9ECEF', boxShadow: 'none' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                <FingerprintIcon /> Consulta RUT Titular
              </Typography>
              
              <Box component="form" onSubmit={handleSearch} sx={{ mt: 2 }}>
                <TextField
                  label="Ingrese RUT del Titular"
                  variant="outlined"
                  fullWidth
                  placeholder="Ej: 199999999 o 19.999.999-9"
                  value={rut}
                  onChange={(e) => setRut(e.target.value)}
                  sx={{ mb: 2 }}
                />
                
                {errorMsg && (
                  <Alert severity="error" sx={{ mb: 2, '& .MuiAlert-message': { fontSize: '0.8rem' } }}>
                    {errorMsg}
                  </Alert>
                )}

                <Button
                  variant="contained"
                  color="primary"
                  fullWidth
                  type="submit"
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                >
                  {loading ? 'Buscando...' : 'Buscar Datos Personales'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Results Pane */}
        <Grid size={{ xs: 12, md: 8 }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : searched && result ? (
            <Box>
              {result.resumen.archivos_involucrados > 0 ? (
                <Box>
                  {/* Summary Card */}
                  <Card sx={{ mb: 3, borderLeft: '4px solid #DC3545', boxShadow: 'none' }}>
                    <CardContent sx={{ p: 3 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6" sx={{ fontWeight: 700 }}>
                          Resumen del Titular: {result.rut_consultado}
                        </Typography>
                        <PiiRiskBadge level={result.resumen.nivel_riesgo_ley21719} size="medium" />
                      </Box>
                      <Divider sx={{ mb: 2 }} />
                      <Grid container spacing={2}>
                        <Grid size={6}>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>DOCUMENTOS AFECTADOS</Typography>
                          <Typography variant="h6" sx={{ fontWeight: 700 }}>{result.resumen.archivos_involucrados}</Typography>
                        </Grid>
                        <Grid size={6}>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>ALERTAS DE DATOS SENSIBLES</Typography>
                          <Typography variant="h6" sx={{ fontWeight: 700, color: 'error.main' }}>{result.resumen.alertas_datos_sensibles}</Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>

                  {/* Document Breakdown Map */}
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2 }}>
                    Mapa de Datos por Documento
                  </Typography>

                  {Object.entries(result.mapa_de_datos).map(([docName, findings]) => (
                    <Card key={docName} sx={{ mb: 2, border: '1px solid #E9ECEF', boxShadow: 'none' }}>
                      <CardContent sx={{ p: 2.5 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                          <ArticleIcon color="action" />
                          <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                            {docName}
                          </Typography>
                        </Box>
                        <Divider />
                        
                        <List sx={{ p: 0 }}>
                          {findings.map((item, idx) => (
                            <ListItem
                              key={idx}
                              sx={{
                                borderBottom: idx < findings.length - 1 ? '1px solid #E9ECEF' : 'none',
                                px: 1,
                                py: 1.5,
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                              }}
                            >
                              <ListItemText
                                primary={
                                  <PiiEntityIcon entityType={item.categoria_legal} showLabel size="small" />
                                }
                              />
                              <Box sx={{ textAlign: 'right' }}>
                                <Typography variant="body2" sx={{ fontWeight: 700, color: 'error.main' }}>
                                  {item.dato_encontrado}
                                </Typography>
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                  {item.estado_almacenamiento}
                                </Typography>
                              </Box>
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              ) : (
                <Alert severity="info">
                  No se encontraron hallazgos registrados para el RUT <strong>{result.rut_consultado}</strong> en la base de datos local.
                </Alert>
              )}
            </Box>
          ) : searched ? (
            <Alert severity="warning">
              No se obtuvieron resultados de la búsqueda.
            </Alert>
          ) : (
            <Paper variant="outlined" sx={{ py: 6, textAlign: 'center', border: '1px dashed #E9ECEF' }}>
              <FingerprintIcon sx={{ fontSize: 48, color: 'text.secondary', opacity: 0.5, mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                Ingrese el RUT de un ciudadano chileno a la izquierda para iniciar el mapeo ARCO/DSAR.
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default DsarLookupPage;
