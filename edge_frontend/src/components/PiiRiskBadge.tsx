import React from 'react';
import Chip from '@mui/material/Chip';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

interface PiiRiskBadgeProps {
  level: 'ALTO' | 'MODERADO' | 'LIMPIO';
  size?: 'small' | 'medium';
}

const PiiRiskBadge: React.FC<PiiRiskBadgeProps> = ({ level, size = 'small' }) => {
  const config = {
    ALTO: {
      bg: '#DC3545',
      text: '#FFFFFF',
      icon: <WarningIcon style={{ fontSize: size === 'small' ? 14 : 18 }} />,
    },
    MODERADO: {
      bg: '#FFC107',
      text: '#343A40',
      icon: <InfoIcon style={{ fontSize: size === 'small' ? 14 : 18 }} />,
    },
    LIMPIO: {
      bg: '#28A745',
      text: '#FFFFFF',
      icon: <CheckCircleIcon style={{ fontSize: size === 'small' ? 14 : 18 }} />,
    },
  };

  const current = config[level] || config.LIMPIO;

  return (
    <Chip
      icon={current.icon}
      label={level}
      size={size}
      sx={{
        backgroundColor: current.bg,
        color: current.text,
        fontWeight: 700,
        fontSize: size === 'small' ? '0.75rem' : '0.875rem',
        borderRadius: '4px',
        '& .MuiChip-icon': { color: current.text },
      }}
    />
  );
};

export default PiiRiskBadge;
