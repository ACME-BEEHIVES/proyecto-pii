import React, { useEffect, useState, useMemo } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Drawer from '@mui/material/Drawer';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Avatar from '@mui/material/Avatar';
import Chip from '@mui/material/Chip';
import Tooltip from '@mui/material/Tooltip';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import { DataGrid } from '@mui/x-data-grid';
import type { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';

// Icons
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import CloseIcon from '@mui/icons-material/Close';
import DescriptionIcon from '@mui/icons-material/Description';
import HubIcon from '@mui/icons-material/Hub';
import EmailIcon from '@mui/icons-material/Email';
import PersonIcon from '@mui/icons-material/Person';
import PhoneIcon from '@mui/icons-material/Phone';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import SearchIcon from '@mui/icons-material/Search';

import { api } from '../services/api';
import type { IdentitySubject } from '../types';
import PiiRiskBadge from '../components/PiiRiskBadge';

/** Normaliza un RUT eliminando puntos, guiones y espacios, dejando solo dígitos + k/K */
const normalizeRut = (rut: string): string =>
  rut.replace(/[^0-9kK]/g, '').toLowerCase();

const IdentityGraphPage: React.FC = () => {
  const [subjects, setSubjects] = useState<IdentitySubject[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState<IdentitySubject | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [pageSize, setPageSize] = useState(25);
  const [searchQuery, setSearchQuery] = useState('');

  /** Filtra los sujetos por RUT (normalizado) o nombre */
  const filteredSubjects = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return subjects;
    const qNorm = normalizeRut(q);
    return subjects.filter((s) => {
      // Match por RUT normalizado (sin puntos ni guion)
      if (normalizeRut(s.rut).includes(qNorm)) return true;
      // Match por nombre (case-insensitive)
      if (s.names.some((n) => n.toLowerCase().includes(q))) return true;
      // Match por email
      if (s.emails.some((e) => e.toLowerCase().includes(q))) return true;
      return false;
    });
  }, [subjects, searchQuery]);

  const fetchSubjects = async () => {
    try {
      setLoading(true);
      const data = await api.getIdentitySubjects();
      setSubjects(data);
    } catch (e) {
      console.error('Error fetching identity subjects', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubjects();
  }, []);

  const handleRowClick = (subject: IdentitySubject) => {
    setSelectedSubject(subject);
    setDrawerOpen(true);
  };

  const columns: GridColDef[] = [
    {
      field: 'rut',
      headerName: 'RUT Titular',
      width: 140,
      renderCell: (params: GridRenderCellParams<IdentitySubject, string>) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 700 }}>
          <FingerprintIcon color="primary" sx={{ fontSize: 18 }} />
          {params.value}
        </Box>
      ),
    },
    {
      field: 'names',
      headerName: 'Nombres Asociados',
      flex: 1.5,
      minWidth: 200,
      renderCell: (params: GridRenderCellParams<IdentitySubject, string[]>) => {
        const list = params.value || [];
        if (list.length === 0) return <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>Sin nombre identificado</Typography>;
        return (
          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', py: 0.5 }}>
            {list.slice(0, 2).map((name, i) => (
              <Chip key={i} label={name} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.75rem' }} />
            ))}
            {list.length > 2 && (
              <Chip label={`+${list.length - 2}`} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.75rem', bgcolor: 'action.hover' }} />
            )}
          </Box>
        );
      },
    },
    {
      field: 'emails',
      headerName: 'Correos Asociados',
      flex: 1.2,
      minWidth: 180,
      renderCell: (params: GridRenderCellParams<IdentitySubject, string[]>) => {
        const list = params.value || [];
        if (list.length === 0) return <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>Sin correo</Typography>;
        return (
          <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
            {list.join(', ')}
          </Typography>
        );
      },
    },
    {
      field: 'findings_count',
      headerName: 'Hallazgos Totales',
      width: 130,
      align: 'center',
      headerAlign: 'center',
    },
    {
      field: 'files',
      headerName: 'Archivos Relac.',
      width: 120,
      align: 'center',
      headerAlign: 'center',
      renderCell: (params: GridRenderCellParams<IdentitySubject, string[]>) => (
        <span>{(params.value || []).length} archivos</span>
      ),
    },
    {
      field: 'risk_level',
      headerName: 'Nivel Riesgo',
      width: 130,
      renderCell: (params: GridRenderCellParams<IdentitySubject, string>) => {
        const val = params.value;
        const level: 'ALTO' | 'MODERADO' | 'LIMPIO' = (val === 'ALTO' || val === 'MODERADO' || val === 'LIMPIO') ? val : 'MODERADO';
        return <PiiRiskBadge level={level} />;
      },
    },
    {
      field: 'actions',
      headerName: 'Acción',
      width: 120,
      sortable: false,
      renderCell: (params: GridRenderCellParams<IdentitySubject>) => (
        <Button
          size="small"
          variant="outlined"
          onClick={() => handleRowClick(params.row)}
          endIcon={<HubIcon sx={{ fontSize: 12 }} />}
        >
          Ver Grafo
        </Button>
      ),
    },
  ];

  // Helper to render interactive connection graph in drawer
  const renderIdentityGraphSvg = (sub: IdentitySubject) => {
    const files = sub.files || [];
    const N = files.length;
    const centerX = 200;
    const centerY = 180;
    const radius = 110;

    // Calculate node coordinates
    const nodes = files.map((file, idx) => {
      const angle = N > 1 ? idx * (2 * Math.PI / N) - Math.PI / 2 : 0;
      return {
        name: file,
        path: sub.file_paths[idx],
        x: centerX + (N > 1 ? radius * Math.cos(angle) : 0),
        y: centerY + (N > 1 ? radius * Math.sin(angle) : -radius),
      };
    });

    return (
      <Box sx={{ position: 'relative', width: '100%', height: 360, bgcolor: '#FAFBFD', borderRadius: 2, border: '1px solid #E9ECEF', overflow: 'hidden', my: 2 }}>
        {/* SVG lines for connections */}
        <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 1 }}>
          <defs>
            <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#007BFF" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#DC3545" stopOpacity="0.4" />
            </linearGradient>
          </defs>
          {nodes.map((node, i) => (
            <line
              key={i}
              x1={centerX}
              y1={centerY}
              x2={node.x}
              y2={node.y}
              stroke="url(#lineGrad)"
              strokeWidth="2"
              strokeDasharray="4 2"
              style={{
                animation: 'dash 10s linear infinite',
              }}
            />
          ))}
        </svg>

        {/* Center Node (Subject) */}
        <Tooltip title={`Sujeto RUT: ${sub.rut}`} arrow>
          <Box
            sx={{
              position: 'absolute',
              left: centerX - 32,
              top: centerY - 32,
              width: 64,
              height: 64,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #007BFF 0%, #0056B3 100%)',
              boxShadow: '0 4px 12px rgba(0, 123, 255, 0.3)',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              zIndex: 2,
              cursor: 'pointer',
              border: '3px solid #FFFFFF',
              transition: 'transform 0.2s',
              '&:hover': { transform: 'scale(1.1)' }
            }}
          >
            <FingerprintIcon sx={{ color: '#FFFFFF', fontSize: 32 }} />
          </Box>
        </Tooltip>

        {/* Outer Nodes (Files) */}
        {nodes.map((node, i) => (
          <Tooltip key={i} title={node.path} arrow>
            <Box
              sx={{
                position: 'absolute',
                left: node.x - 22,
                top: node.y - 22,
                width: 44,
                height: 44,
                borderRadius: '50%',
                bgcolor: '#FFFFFF',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                zIndex: 2,
                cursor: 'pointer',
                border: '2px solid #E9ECEF',
                transition: 'transform 0.2s, border-color 0.2s',
                '&:hover': { 
                  transform: 'scale(1.15)',
                  borderColor: 'primary.main'
                }
              }}
            >
              <DescriptionIcon color="primary" sx={{ fontSize: 20 }} />
            </Box>
          </Tooltip>
        ))}

        {/* Dynamic Labels */}
        {nodes.map((node, i) => {
          // Adjust text position slightly below/above the node
          const isBelow = node.y > centerY;
          return (
            <Typography
              key={`label-${i}`}
              variant="caption"
              sx={{
                position: 'absolute',
                left: node.x - 60,
                top: node.y + (isBelow ? 26 : -38),
                width: 120,
                textAlign: 'center',
                fontWeight: 600,
                color: 'text.primary',
                textShadow: '0 1px 2px #FFFFFF',
                bgcolor: 'rgba(255, 255, 255, 0.7)',
                px: 0.5,
                borderRadius: 1,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                pointerEvents: 'none',
                zIndex: 3
              }}
            >
              {node.name}
            </Typography>
          );
        })}

        {/* Center avatar text label */}
        <Typography
          variant="caption"
          sx={{
            position: 'absolute',
            left: centerX - 60,
            top: centerY + 36,
            width: 120,
            textAlign: 'center',
            fontWeight: 700,
            color: 'primary.main',
            bgcolor: 'rgba(255,255,255,0.9)',
            borderRadius: 1,
            py: 0.25,
            border: '1px solid #E9ECEF',
            zIndex: 3
          }}
        >
          {sub.rut}
        </Typography>
      </Box>
    );
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <HubIcon color="primary" sx={{ fontSize: 36 }} /> Gráfico de Identidad (Sujetos PII)
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Correlación inteligente de RUTs, nombres y correos de la Ley 21.719 distribuidos en múltiples archivos y fuentes
        </Typography>
      </Box>

      {/* Buscador por RUT o Nombre */}
      <Card sx={{ border: '1px solid #E9ECEF', boxShadow: 'none', mb: 2, p: 2 }}>
        <TextField
          id="identity-search"
          fullWidth
          size="small"
          placeholder="Buscar por RUT (ej: 8.565.137-4 o 8565137), nombre o correo…"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            },
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
              bgcolor: '#FAFBFD',
            },
          }}
        />
        {searchQuery && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
            {filteredSubjects.length} de {subjects.length} titulares encontrados
          </Typography>
        )}
      </Card>

      <Card sx={{ border: '1px solid #E9ECEF', boxShadow: 'none' }}>
        <Box sx={{ height: 650, width: '100%' }}>
          <DataGrid
            rows={filteredSubjects}
            getRowId={(row) => row.rut}
            columns={columns}
            loading={loading}
            initialState={{
              pagination: { paginationModel: { pageSize } },
            }}
            pageSizeOptions={[10, 25, 50]}
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

      {/* Detail & Graph Drawer */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
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
        {selectedSubject && (
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                <HubIcon color="primary" /> Grafo de Relación del Titular
              </Typography>
              <IconButton onClick={() => setDrawerOpen(false)}>
                <CloseIcon />
              </IconButton>
            </Box>
            <Divider sx={{ mb: 3 }} />

            <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
              {/* Profile Card */}
              <Card variant="outlined" sx={{ mb: 3, bgcolor: '#FAFBFD' }}>
                <CardContent sx={{ p: 2.5, display: 'flex', alignItems: 'center', gap: 2.5 }}>
                  <Avatar sx={{ bgcolor: selectedSubject.risk_level === 'ALTO' ? 'error.main' : 'warning.main', width: 56, height: 56 }}>
                    <PersonIcon sx={{ fontSize: 32 }} />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
                      {selectedSubject.names[0] || 'Nombre No Identificado'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                      <FingerprintIcon sx={{ fontSize: 16 }} /> {selectedSubject.rut}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>

              {/* Connected Files Graph */}
              <Typography variant="subtitle2" sx={{ fontWeight: 700 }} gutterBottom>
                Mapa de Datos Asociados (Archivos Relacionados)
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Este gráfico mapea la identidad del titular con las rutas del host donde se identificó su información.
              </Typography>

              {renderIdentityGraphSvg(selectedSubject)}

              {/* Data Details list */}
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5 }}>
                  Nombres alternativos identificados:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 3 }}>
                  {selectedSubject.names.map((name, i) => (
                    <Chip key={i} icon={<PersonIcon />} label={name} color="default" variant="outlined" />
                  ))}
                  {selectedSubject.names.length === 0 && (
                    <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>Ninguno</Typography>
                  )}
                </Box>

                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5 }}>
                  Correos asociados:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 3 }}>
                  {selectedSubject.emails.map((email, i) => (
                    <Chip key={i} icon={<EmailIcon />} label={email} color="primary" variant="outlined" />
                  ))}
                  {selectedSubject.emails.length === 0 && (
                    <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>Ninguno</Typography>
                  )}
                </Box>

                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5 }}>
                  Teléfonos asociados:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 3 }}>
                  {(selectedSubject.phones || []).map((phone, i) => (
                    <Chip key={i} icon={<PhoneIcon />} label={phone} color="info" variant="outlined" />
                  ))}
                  {(!selectedSubject.phones || selectedSubject.phones.length === 0) && (
                    <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>Ninguno</Typography>
                  )}
                </Box>

                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5 }}>
                  Fechas de nacimiento asociadas:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 3 }}>
                  {(selectedSubject.birth_dates || []).map((bdate, i) => (
                    <Chip key={i} icon={<CalendarTodayIcon />} label={bdate} color="warning" variant="outlined" />
                  ))}
                  {(!selectedSubject.birth_dates || selectedSubject.birth_dates.length === 0) && (
                    <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>Ninguno</Typography>
                  )}
                </Box>

                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                  Archivos involucrados ({selectedSubject.files.length}):
                </Typography>
                <Box sx={{ border: '1px solid #E9ECEF', borderRadius: 1.5, overflow: 'hidden' }}>
                  {selectedSubject.files.map((file, i) => (
                    <Box 
                      key={i} 
                      sx={{ 
                        p: 1.5, 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: 1.5, 
                        borderBottom: i < selectedSubject.files.length - 1 ? '1px solid #E9ECEF' : 'none',
                        bgcolor: 'background.paper',
                        '&:hover': { bgcolor: 'action.hover' }
                      }}
                    >
                      <DescriptionIcon color="action" />
                      <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
                        <Typography variant="body2" sx={{ fontWeight: 600, textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                          {file}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap', fontFamily: 'monospace' }}>
                          {selectedSubject.file_paths[i]}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              </Box>
            </Box>
          </Box>
        )}
      </Drawer>
    </Box>
  );
};

export default IdentityGraphPage;
