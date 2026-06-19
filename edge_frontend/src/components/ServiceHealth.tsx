import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import CircleIcon from '@mui/icons-material/Circle';
import StorageIcon from '@mui/icons-material/Storage';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import PolicyIcon from '@mui/icons-material/Policy';
import SettingsInputHdmiIcon from '@mui/icons-material/SettingsInputHdmi';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { api } from '../services/api';
import type { HealthResponse } from '../types';

const ServiceHealth: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  const fetchHealth = async () => {
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch {
      setHealth({
        status: 'error',
        service: 'upshield-edge-agent',
        version: '1.0.0',
        environment: 'development',
        services: {
          database: { status: 'unhealthy', message: 'API Backend no responde' },
          tika: { status: 'unhealthy', message: 'API Backend no responde' },
          presidio: { status: 'unhealthy', message: 'API Backend no responde' },
          watcher: { status: 'unhealthy', message: 'API Backend no responde' },
        },
      });
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: 'healthy' | 'unhealthy' | 'degraded') => {
    if (status === 'healthy') return '#28A745';
    if (status === 'degraded') return '#FFC107';
    return '#DC3545';
  };

  const getStatusLabel = (status: 'healthy' | 'unhealthy' | 'degraded') => {
    if (status === 'healthy') return 'Conectado';
    if (status === 'degraded') return 'Degradado';
    return 'Sin Conexión';
  };

  const renderService = (
    label: string,
    status: 'healthy' | 'unhealthy' | 'degraded',
    icon: React.ReactNode,
    message: string | null
  ) => {
    return (
      <Tooltip title={message || getStatusLabel(status)} placement="right" arrow>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            py: 0.75,
            px: 1.5,
            borderRadius: '6px',
            backgroundColor: 'rgba(255, 255, 255, 0.04)',
            mb: 0.75,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {icon}
            <Typography variant="body2" sx={{ color: '#CED4DA', fontSize: '0.85rem' }}>
              {label}
            </Typography>
          </Box>
          <CircleIcon sx={{ color: getStatusColor(status), fontSize: 10 }} />
        </Box>
      </Tooltip>
    );
  };

  const dbStatus = health?.services?.database?.status || 'unhealthy';
  const dbMsg = health?.services?.database?.message || null;

  const tikaStatus = health?.services?.tika?.status || 'unhealthy';
  const tikaMsg = health?.services?.tika?.message || null;

  const presidioStatus = health?.services?.presidio?.status || 'unhealthy';
  const presidioMsg = health?.services?.presidio?.message || null;

  const watcherStatus = health?.services?.watcher?.status || 'unhealthy';
  const watcherMsg = health?.services?.watcher?.message || null;

  const backendStatus = health ? ('healthy' as const) : ('unhealthy' as const);

  return (
    <Box sx={{ p: 2, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
      <Typography variant="caption" sx={{ color: '#6C757D', display: 'block', mb: 1.5, fontWeight: 600, letterSpacing: '0.05em' }}>
        ESTADO DE SERVICIOS
      </Typography>

      {renderService(
        'Edge Agent API',
        backendStatus,
        <SettingsInputHdmiIcon sx={{ color: '#CED4DA', fontSize: 16 }} />,
        backendStatus === 'healthy' ? 'API Operativa' : 'No hay conexión con el backend'
      )}

      {renderService(
        'Base de Datos (MySQL)',
        dbStatus,
        <StorageIcon sx={{ color: '#CED4DA', fontSize: 16 }} />,
        dbMsg
      )}

      {renderService(
        'Apache Tika (Text)',
        tikaStatus,
        <ReceiptLongIcon sx={{ color: '#CED4DA', fontSize: 16 }} />,
        tikaMsg
      )}

      {renderService(
        'Presidio NLP (PII)',
        presidioStatus,
        <PolicyIcon sx={{ color: '#CED4DA', fontSize: 16 }} />,
        presidioMsg
      )}

      {renderService(
        'Monitoreo Tiempo Real',
        watcherStatus,
        <VisibilityIcon sx={{ color: '#CED4DA', fontSize: 16 }} />,
        watcherMsg
      )}
    </Box>
  );
};

export default ServiceHealth;
