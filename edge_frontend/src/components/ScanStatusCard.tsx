import React, { useEffect, useState } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import LinearProgress from '@mui/material/LinearProgress';
import CircularProgress from '@mui/material/CircularProgress';
import Tooltip from '@mui/material/Tooltip';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircle';
import ErrorOutlineIcon from '@mui/icons-material/Error';
import FolderIcon from '@mui/icons-material/Folder';
import HelpOutlineIcon from '@mui/icons-material/HelpOutlined';
import { api } from '../services/api';
import type { ScanJob } from '../types';

const ScanStatusCard: React.FC = () => {
  const [job, setJob] = useState<ScanJob | null>(null);
  const [polling, setPolling] = useState(false);

  const fetchStatus = async () => {
    try {
      const data = await api.getScanStatus();
      setJob(data);
      if (data && (data.status === 'running' || data.status === 'pending')) {
        setPolling(true);
      } else {
        setPolling(false);
      }
    } catch (e) {
      console.error('Error fetching scan status', e);
      setPolling(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  useEffect(() => {
    let interval: any;
    if (polling) {
      interval = setInterval(fetchStatus, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [polling]);

  const handleStart = async () => {
    try {
      const newJob = await api.startScan();
      setJob(newJob);
      setPolling(true);
    } catch (e) {
      console.error('Error starting scan', e);
      alert('No se pudo iniciar el escaneo. Verifica el estado de los servicios.');
    }
  };

  const handleStop = async () => {
    if (!job) return;
    try {
      await api.stopScan(job.id);
      fetchStatus();
    } catch (e) {
      console.error('Error stopping scan', e);
    }
  };

  const getProgress = () => {
    if (!job || job.files_total === 0) return 0;
    const processed = job.files_scanned + job.files_skipped;
    return Math.round((processed / job.files_total) * 100);
  };

  const renderContent = () => {
    if (!job || (job.status as string) === 'idle') {
      return (
        <Box sx={{ textAlign: 'center', py: 2 }}>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            No hay ningún escaneo activo en este momento.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<PlayArrowIcon />}
            onClick={handleStart}
            sx={{ mt: 1 }}
          >
            Iniciar Escaneo Completo
          </Button>
        </Box>
      );
    }

    const pct = getProgress();

    if (job.status === 'pending' || job.status === 'running') {
      return (
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <CircularProgress size={24} thickness={4} />
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {job.status === 'pending' ? 'Inicializando...' : `Escaneando: ${pct}%`}
              </Typography>
            </Box>
            <Button
              variant="outlined"
              color="error"
              size="small"
              startIcon={<StopIcon />}
              onClick={handleStop}
            >
              Detener
            </Button>
          </Box>
          <LinearProgress variant="determinate" value={pct} sx={{ height: 8, borderRadius: 4, mb: 2 }} />
          
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 2, mt: 2 }}>
            <Box sx={{ textAlign: 'center', p: 1.5, bg: '#F8F9FA', borderRadius: 1, border: '1px dashed #E9ECEF' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">TOTAL ARCHIVOS</Typography>
                <Tooltip title="Total de elementos a analizar (archivos en disco + celdas de bases de datos configuradas)" arrow placement="top">
                  <HelpOutlineIcon sx={{ fontSize: 13, color: 'text.secondary', cursor: 'help' }} />
                </Tooltip>
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>{job.files_total}</Typography>
            </Box>
            <Box sx={{ textAlign: 'center', p: 1.5, bg: '#F8F9FA', borderRadius: 1, border: '1px dashed #E9ECEF' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">ESCANEADOS</Typography>
                <Tooltip title="Elementos nuevos o modificados analizados activamente en esta ejecución" arrow placement="top">
                  <HelpOutlineIcon sx={{ fontSize: 13, color: 'text.secondary', cursor: 'help' }} />
                </Tooltip>
              </Box>
              <Typography variant="h6" color="primary.main" sx={{ fontWeight: 700 }}>{job.files_scanned}</Typography>
            </Box>
            <Box sx={{ textAlign: 'center', p: 1.5, bg: '#F8F9FA', borderRadius: 1, border: '1px dashed #E9ECEF' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">HALLAZGOS PII</Typography>
                <Tooltip title="Detecciones de datos personales sensibles identificadas hasta el momento" arrow placement="top">
                  <HelpOutlineIcon sx={{ fontSize: 13, color: 'text.secondary', cursor: 'help' }} />
                </Tooltip>
              </Box>
              <Typography variant="h6" color="error.main" sx={{ fontWeight: 700 }}>{job.findings_count}</Typography>
            </Box>
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2, fontStyle: 'italic' }}>
            Ruta activa: {job.root_path}
          </Typography>
        </Box>
      );
    }

    if (job.status === 'completed') {
      return (
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
            <CheckCircleOutlineIcon sx={{ color: 'success.main', fontSize: 32 }} />
            <Box>
              <Typography variant="subtitle1" color="success.main" sx={{ fontWeight: 600 }}>
                Escaneo Finalizado Exitosamente
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Terminó el {job.completed_at ? new Date(job.completed_at).toLocaleString() : ''}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(2, 1fr)', 
            gap: 1.5, 
            my: 1.5 
          }}>
            <Box sx={{ textAlign: 'center', p: 1, backgroundColor: '#F8F9FA', borderRadius: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">TOTAL</Typography>
                <Tooltip title="Total de elementos configurados (archivos físicos + celdas de base de datos)" arrow placement="top">
                  <HelpOutlineIcon sx={{ fontSize: 13, color: 'text.secondary', cursor: 'help' }} />
                </Tooltip>
              </Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{job.files_total}</Typography>
            </Box>
            <Box sx={{ textAlign: 'center', p: 1, backgroundColor: '#F8F9FA', borderRadius: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">PROCESADOS</Typography>
                <Tooltip title="Elementos nuevos o modificados analizados en esta ejecución" arrow placement="top">
                  <HelpOutlineIcon sx={{ fontSize: 13, color: 'text.secondary', cursor: 'help' }} />
                </Tooltip>
              </Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{job.files_scanned}</Typography>
            </Box>
            <Box sx={{ textAlign: 'center', p: 1, backgroundColor: '#F8F9FA', borderRadius: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">OMITIDOS</Typography>
                <Tooltip title="Elementos sin cambios (según hash MD5) omitidos por eficiencia (escaneo incremental)" arrow placement="top">
                  <HelpOutlineIcon sx={{ fontSize: 13, color: 'text.secondary', cursor: 'help' }} />
                </Tooltip>
              </Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{job.files_skipped}</Typography>
            </Box>
            <Box sx={{ textAlign: 'center', p: 1, backgroundColor: '#F8F9FA', borderRadius: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">PII HALLADOS</Typography>
                <Tooltip title="Hallazgos de datos personales detectados en esta ejecución" arrow placement="top">
                  <HelpOutlineIcon sx={{ fontSize: 13, color: 'text.secondary', cursor: 'help' }} />
                </Tooltip>
              </Box>
              <Typography variant="subtitle1" color={job.findings_count > 0 ? 'error.main' : 'success.main'} sx={{ fontWeight: 700 }}>
                {job.findings_count}
              </Typography>
            </Box>
          </Box>

          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.5, fontStyle: 'italic', textAlign: 'center' }}>
            Nota: El escáner es incremental y omite elementos sin cambios. Si la suma no cuadra con el total, algunos elementos no pudieron ser procesados o leídos.
          </Typography>

          <Box sx={{ display: 'flex', gap: 1.5, justifyContent: 'center', mt: 2.5 }}>
            <Button variant="contained" color="primary" onClick={handleStart} startIcon={<PlayArrowIcon />}>
              Escanear de Nuevo
            </Button>
          </Box>
        </Box>
      );
    }

    // failed or cancelled
    return (
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
          <ErrorOutlineIcon sx={{ color: 'error.main', fontSize: 32 }} />
          <Box>
            <Typography variant="subtitle1" color="error.main" sx={{ fontWeight: 600 }}>
              {job.status === 'cancelled' ? 'Escaneo Cancelado' : 'Escaneo Fallido'}
            </Typography>
            {job.error_message && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {job.error_message}
              </Typography>
            )}
          </Box>
        </Box>
        <Box sx={{ display: 'flex', gap: 1.5, justifyContent: 'center', mt: 2 }}>
          <Button variant="contained" color="primary" onClick={handleStart} startIcon={<PlayArrowIcon />}>
            Reintentar Escaneo
          </Button>
        </Box>
      </Box>
    );
  };

  return (
    <Card sx={{ border: '1px solid #E9ECEF', boxShadow: 'none' }}>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
          <FolderIcon color="action" /> Estado del Escáner
        </Typography>
        <Box sx={{ mt: 2 }}>{renderContent()}</Box>
      </CardContent>
    </Card>
  );
};

export default ScanStatusCard;
