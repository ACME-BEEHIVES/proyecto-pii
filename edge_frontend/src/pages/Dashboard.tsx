import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import MuiTooltip from '@mui/material/Tooltip';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';

// Icons
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import PolicyIcon from '@mui/icons-material/Policy';
import GavelIcon from '@mui/icons-material/Gavel';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import StorageIcon from '@mui/icons-material/Storage';

import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

import { api } from '../services/api';
import type { FindingsStats, ScanFinding } from '../types';
import PiiRiskBadge from '../components/PiiRiskBadge';
import PiiEntityIcon from '../components/PiiEntityIcon';
import ScanStatusCard from '../components/ScanStatusCard';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<FindingsStats | null>(null);
  const [recentFindings, setRecentFindings] = useState<ScanFinding[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const statsData = await api.getFindingsStats();
      setStats(statsData);

      const recent = await api.getFindings({ limit: 5 });
      setRecentFindings(recent);
    } catch (e) {
      console.error('Error loading dashboard data', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  // Fallback default stats if none found
  const dataStats = stats || {
    total_findings: 0,
    active_findings: 0,
    resolved_findings: 0,
    files_scanned: 0,
    scanned_files_count: 0,
    scanned_db_cells_count: 0,
    active_db_configs_count: 0,
    findings_in_files_count: 0,
    findings_in_db_count: 0,
    by_type: {},
    by_severity: { ALTO: 0, MODERADO: 0, LIMPIO: 1 },
    by_folder: {},
    global_risk_level: 'LIMPIO' as const,
  };

  const riskLevel = dataStats.global_risk_level || 'LIMPIO';
  const hasHighRisk = riskLevel === 'ALTO';
  const hasModerateRisk = riskLevel === 'MODERADO';

  // Format entity type pie data
  const pieData = Object.entries(dataStats.by_type).map(([key, value]) => {
    const labelMap: Record<string, string> = {
      CHILE_RUT: 'RUT',
      EMAIL_ADDRESS: 'Email',
      PERSON: 'Persona',
      DATA_SALUD: 'Salud',
      DATA_ETNIA: 'Etnia',
      DATA_POLITICA: 'Política',
      DATA_RELIGION: 'Religión',
      DATA_SEXUALIDAD: 'Sexualidad',
      DATA_SINDICAL: 'Sindical',
      DATA_SOCIOECONOMICO: 'Socioeconómico',
      DATA_IDEOLOGIA: 'Ideología',
      DATA_BIOLOGICO: 'Biológico',
      DATA_BIOMETRICO: 'Biométrico',
    };
    const colorMap: Record<string, string> = {
      CHILE_RUT: '#4A5568',     // Dark Slate Grey
      EMAIL_ADDRESS: '#718096', // Medium Cool Grey
      PERSON: '#A0AEC0',        // Light Grey
      DATA_SALUD: '#DC3545',
      DATA_ETNIA: '#E67E22',
      DATA_POLITICA: '#8E44AD',
      DATA_RELIGION: '#2980B9',
      DATA_SEXUALIDAD: '#E91E63',
      DATA_SINDICAL: '#E67E22',
      DATA_SOCIOECONOMICO: '#2ECC71',
      DATA_IDEOLOGIA: '#9B59B6',
      DATA_BIOLOGICO: '#1ABC9C',
      DATA_BIOMETRICO: '#E74C3C',
    };
    return {
      name: labelMap[key] || key,
      value,
      color: colorMap[key] || '#6C757D',
    };
  });

  // Bar chart by folder/path and database connection/table
  const barData = Object.entries(dataStats.by_folder).map(([key, value]) => {
    const isDb = key.startsWith('db://');
    let displayName: string;
    let fullPath: string;
    if (isDb) {
      const parts = key.replace('db://', '').split('/');
      displayName = parts[parts.length - 1] || key; // table name only
      fullPath = parts.join(' : ');
    } else {
      const normalized = key.replace(/\\/g, '/');
      const parts = normalized.split('/');
      displayName = parts.pop() || normalized; // folder name only
      fullPath = normalized;
    }
    return {
      folder: displayName,
      fullPath,
      hallazgos: value,
      isDb,
    };
  }).sort((a, b) => b.hallazgos - a.hallazgos).slice(0, 6);

  const kpis = [
    {
      title: 'Archivos Escaneados',
      value: dataStats.scanned_files_count,
      icon: <InsertDriveFileIcon sx={{ fontSize: 32, color: 'primary.main' }} />,
      desc: 'En directorios locales/red',
      tooltip: 'Cantidad total de archivos físicos (PDF, Word, TXT, Excel, Imágenes) analizados en los directorios locales o de red configurados.',
    },
    {
      title: 'Celdas de BD Escaneadas',
      value: dataStats.scanned_db_cells_count,
      icon: <StorageIcon sx={{ fontSize: 32, color: '#E67E22' }} />,
      desc: `${dataStats.active_db_configs_count} base de datos activa${dataStats.active_db_configs_count !== 1 ? 's' : ''}`,
      tooltip: 'Total de celdas (valores de columnas de texto) escaneadas en las tablas de las bases de datos SQL conectadas.',
    },
    {
      title: 'Hallazgos Activos',
      value: dataStats.active_findings,
      icon: <PolicyIcon sx={{ fontSize: 32, color: 'error.main' }} />,
      desc: `${dataStats.findings_in_files_count} en archivos · ${dataStats.findings_in_db_count} en BD`,
      tooltip: 'Número de datos personales (PII) detectados en el último escaneo que no han sido marcados como resueltos. Se muestra el desglose de hallazgos en archivos físicos y celdas de bases de datos.',
    },
    {
      title: 'Riesgo del Agente',
      value: riskLevel,
      icon: <GavelIcon sx={{ fontSize: 32, color: hasHighRisk ? 'error.main' : hasModerateRisk ? 'warning.main' : 'success.main' }} />,
      isRisk: true,
      desc: `${dataStats.by_severity.ALTO || 0} hallazgos críticos (Alto Riesgo)`,
      tooltip: 'Evaluación de riesgo general de la red basada en el tipo y la cantidad de PII expuesta. Se eleva a ALTO si se detecta cualquier dato de categoría sensible (salud, etnia, ideología, etc.) sin resolver.',
    },
    {
      title: 'Casos Resueltos',
      value: dataStats.resolved_findings,
      icon: <CheckCircleIcon sx={{ fontSize: 32, color: 'success.main' }} />,
      desc: 'Mitigados correctamente',
      tooltip: 'Total de hallazgos que han sido resueltos (ya sea porque el archivo/dato fue eliminado, corregido o marcado como gestionado).',
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
            Panel de Control
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Monitoreo y diagnóstico de datos personales (PII) on-premise
          </Typography>
        </Box>
        <Button variant="outlined" onClick={loadData}>
          Actualizar Datos
        </Button>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {kpis.map((kpi, idx) => (
          <Grid key={idx} size={{ xs: 12, sm: 6, md: 4, lg: 2.4 }} sx={{ display: 'flex' }}>
            <Card sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', borderLeft: kpi.isRisk ? `4px solid ${hasHighRisk ? '#DC3545' : hasModerateRisk ? '#FFC107' : '#28A745'}` : 'none' }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', p: 3, flexGrow: 1 }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between', width: '100%' }}>
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                        {kpi.title}
                      </Typography>
                      <MuiTooltip title={kpi.tooltip} arrow placement="top">
                        <InfoOutlinedIcon sx={{ fontSize: 16, color: 'text.disabled', cursor: 'pointer' }} />
                      </MuiTooltip>
                    </Box>
                    {kpi.isRisk ? (
                      <Box sx={{ mt: 1 }}>
                        <PiiRiskBadge level={kpi.value as 'ALTO' | 'MODERADO' | 'LIMPIO'} size="medium" />
                      </Box>
                    ) : (
                      <Typography variant="h4" sx={{ fontWeight: 700 }}>
                        {kpi.value}
                      </Typography>
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.5 }}>
                    {kpi.desc}
                  </Typography>
                </Box>
                {kpi.icon}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main Grid: Charts + Scanner Status */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Real-time Scanner Card */}
        <Grid size={{ xs: 12, md: 4 }}>
          <ScanStatusCard />
        </Grid>

        {/* Donut Chart: Entity Distribution */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 700 }} gutterBottom>
                Distribución por Entidad
              </Typography>
              {pieData.length > 0 ? (
                <Box sx={{ height: 260 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        innerRadius={45}
                        outerRadius={65}
                        dataKey="value"
                        paddingAngle={2}
                      >
                        {pieData.map((entry, idx) => (
                          <Cell key={idx} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [`${value} hallazgos`, 'Cantidad']} />
                      <Legend 
                        layout="horizontal" 
                        verticalAlign="bottom" 
                        align="center" 
                        iconSize={8} 
                        iconType="circle"
                        wrapperStyle={{ fontSize: '10px', marginTop: '5px' }} 
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 260 }}>
                  <Typography variant="body2" color="text.secondary">No hay hallazgos registrados</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Bar Chart: Most Affected Sources (Files and Databases) */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Orígenes más Afectados
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Box sx={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#007BFF' }} />
                  <Typography variant="caption" color="text.secondary">Archivos</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Box sx={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#E67E22' }} />
                  <Typography variant="caption" color="text.secondary">Tablas BD</Typography>
                </Box>
              </Box>
              {barData.length > 0 ? (
                <Box sx={{ height: 215 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis 
                        dataKey="folder" 
                        tick={{ fontSize: 9 }} 
                        angle={-25} 
                        textAnchor="end" 
                        height={60} 
                        interval={0} 
                      />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip 
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const data = payload[0].payload;
                            return (
                              <Box sx={{ bgcolor: 'background.paper', p: 1.5, border: '1px solid', borderColor: 'divider', borderRadius: 1, boxShadow: 1 }}>
                                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                  {data.isDb ? 'Base de Datos' : 'Directorio'}
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ wordBreak: 'break-all', mt: 0.5, mb: 1, maxWidth: 260 }}>
                                  {data.fullPath}
                                </Typography>
                                <Typography variant="body2" sx={{ fontWeight: 700, color: 'error.main' }}>
                                  Hallazgos: {data.hallazgos}
                                </Typography>
                              </Box>
                            );
                          }
                          return null;
                        }}
                      />
                      <Bar dataKey="hallazgos" radius={[4, 4, 0, 0]}>
                        {barData.map((entry, idx) => (
                          <Cell key={`cell-${idx}`} fill={entry.isDb ? '#E67E22' : '#007BFF'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 215 }}>
                  <Typography variant="body2" color="text.secondary">No hay orígenes con riesgo</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Latest Findings Table */}
      <Card sx={{ mb: 4 }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2.5 }}>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              Últimos Hallazgos Detectados
            </Typography>
            <Button
              endIcon={<ArrowForwardIcon />}
              onClick={() => navigate('/findings')}
              sx={{ fontWeight: 600 }}
            >
              Ver Todos
            </Button>
          </Box>

          {recentFindings.length > 0 ? (
            <TableContainer component={Paper} variant="outlined" sx={{ border: '1px solid #E9ECEF' }}>
              <Table aria-label="recent findings table">
                <TableHead sx={{ backgroundColor: '#F8F9FA' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Origen / Archivo</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Tipo de Entidad</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Certeza</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Nivel de Riesgo</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Fecha Detección</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentFindings.map((finding) => {
                    const isDb = finding.file_path.startsWith('db://');
                    return (
                      <TableRow key={finding.id} hover>
                        <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {isDb ? (
                              <StorageIcon sx={{ fontSize: 18, color: '#E67E22' }} titleAccess="Origen: Base de Datos" />
                            ) : (
                              <InsertDriveFileIcon sx={{ fontSize: 18, color: 'primary.main' }} titleAccess="Origen: Archivo Físico" />
                            )}
                            <span title={finding.file_path}>{finding.file_name}</span>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <PiiEntityIcon entityType={finding.entity_type} showLabel size="small" />
                        </TableCell>
                        <TableCell>{Math.round(finding.confidence_score * 100)}%</TableCell>
                        <TableCell>
                          <PiiRiskBadge level={finding.is_sensitive ? 'ALTO' : 'MODERADO'} />
                        </TableCell>
                        <TableCell>
                          {new Date(finding.created_at).toLocaleDateString()} {new Date(finding.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4, border: '1px dashed #E9ECEF', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                No hay hallazgos detectados recientemente. Ejecuta un escaneo para analizar tu red.
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard;
