import React from 'react';
import BadgeIcon from '@mui/icons-material/Badge';
import EmailIcon from '@mui/icons-material/Email';
import PersonIcon from '@mui/icons-material/Person';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import GroupsIcon from '@mui/icons-material/Groups';
import GavelIcon from '@mui/icons-material/Gavel';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import FavoriteIcon from '@mui/icons-material/Favorite';
import HelpOutlineIcon from '@mui/icons-material/Help';
import Box from '@mui/material/Box';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import BiotechIcon from '@mui/icons-material/Biotech';
import PsychologyIcon from '@mui/icons-material/Psychology';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import Diversity3Icon from '@mui/icons-material/Diversity3';
import FlightIcon from '@mui/icons-material/Flight';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import QrCode2Icon from '@mui/icons-material/QrCode2';
import PhoneIcon from '@mui/icons-material/Phone';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import HomeIcon from '@mui/icons-material/Home';
import PublicIcon from '@mui/icons-material/Public';
import SecurityIcon from '@mui/icons-material/Security';

interface PiiEntityIconProps {
  entityType: string;
  size?: 'small' | 'medium' | 'large';
  showLabel?: boolean;
}

// eslint-disable-next-line react-refresh/only-export-components
export const ENTITY_CONFIG: Record<string, { icon: React.ReactElement; color: string; label: string; bg: string }> = {
  CHILE_RUT: {
    icon: <BadgeIcon />,
    color: '#6C757D',
    bg: 'rgba(108, 117, 125, 0.1)',
    label: 'RUT',
  },
  EMAIL_ADDRESS: {
    icon: <EmailIcon />,
    color: '#6C757D',
    bg: 'rgba(108, 117, 125, 0.1)',
    label: 'Email',
  },
  PERSON: {
    icon: <PersonIcon />,
    color: '#6C757D',
    bg: 'rgba(108, 117, 125, 0.1)',
    label: 'Persona',
  },
  DATA_SALUD: {
    icon: <LocalHospitalIcon />,
    color: '#DC3545',
    bg: 'rgba(220, 53, 69, 0.1)',
    label: 'Salud',
  },
  DATA_ETNIA: {
    icon: <GroupsIcon />,
    color: '#E67E22',
    bg: 'rgba(230, 126, 34, 0.1)',
    label: 'Etnia',
  },
  DATA_POLITICA: {
    icon: <GavelIcon />,
    color: '#8E44AD',
    bg: 'rgba(142, 68, 173, 0.1)',
    label: 'Política',
  },
  DATA_RELIGION: {
    icon: <AccountBalanceIcon />,
    color: '#2980B9',
    bg: 'rgba(41, 128, 185, 0.1)',
    label: 'Religión',
  },
  DATA_SEXUALIDAD: {
    icon: <FavoriteIcon />,
    color: '#E91E63',
    bg: 'rgba(233, 30, 99, 0.1)',
    label: 'Sexualidad',
  },
  DATA_SINDICAL: {
    icon: <Diversity3Icon />,
    color: '#E67E22',
    bg: 'rgba(230, 126, 34, 0.1)',
    label: 'Sindical',
  },
  DATA_SOCIOECONOMICO: {
    icon: <AccountBalanceWalletIcon />,
    color: '#2ECC71',
    bg: 'rgba(46, 204, 113, 0.1)',
    label: 'Socioeconómico',
  },
  DATA_IDEOLOGIA: {
    icon: <PsychologyIcon />,
    color: '#9B59B6',
    bg: 'rgba(155, 89, 182, 0.1)',
    label: 'Ideología',
  },
  DATA_BIOLOGICO: {
    icon: <BiotechIcon />,
    color: '#1ABC9C',
    bg: 'rgba(26, 188, 156, 0.1)',
    label: 'Biológico',
  },
  DATA_BIOMETRICO: {
    icon: <FingerprintIcon />,
    color: '#E74C3C',
    bg: 'rgba(231, 76, 60, 0.1)',
    label: 'Biométrico',
  },
  PHONE_NUMBER: {
    icon: <PhoneIcon />,
    color: '#6C757D',
    bg: 'rgba(108, 117, 125, 0.1)',
    label: 'Teléfono',
  },
  DATE_TIME: {
    icon: <CalendarTodayIcon />,
    color: '#6C757D',
    bg: 'rgba(108, 117, 125, 0.1)',
    label: 'Fecha',
  },
  DOMICILIO: {
    icon: <HomeIcon />,
    color: '#6C757D',
    bg: 'rgba(108, 117, 125, 0.1)',
    label: 'Domicilio',
  },
  NACIONALIDAD: {
    icon: <PublicIcon />,
    color: '#6C757D',
    bg: 'rgba(108, 117, 125, 0.1)',
    label: 'Nacionalidad',
  },
  DATA_PENAL: {
    icon: <SecurityIcon />,
    color: '#C0392B',
    bg: 'rgba(192, 57, 43, 0.1)',
    label: 'Penal',
  },
  PASAPORTE: {
    icon: <FlightIcon />,
    color: '#2471A3',
    bg: 'rgba(36, 113, 163, 0.1)',
    label: 'Pasaporte',
  },
  LICENCIA_CONDUCIR: {
    icon: <DirectionsCarIcon />,
    color: '#1E8449',
    bg: 'rgba(30, 132, 73, 0.1)',
    label: 'Licencia Conducir',
  },
  CUENTA_BANCARIA: {
    icon: <CreditCardIcon />,
    color: '#D4AC0D',
    bg: 'rgba(212, 172, 13, 0.1)',
    label: 'Cuenta Bancaria',
  },
  NUMERO_SERIE_DOC: {
    icon: <QrCode2Icon />,
    color: '#7D3C98',
    bg: 'rgba(125, 60, 152, 0.1)',
    label: 'N° Serie Doc.',
  },
};

const PiiEntityIcon: React.FC<PiiEntityIconProps> = ({ entityType, size = 'medium', showLabel = false }) => {
  const current = ENTITY_CONFIG[entityType] || {
    icon: <HelpOutlineIcon />,
    color: '#6C757D',
    bg: 'rgba(108, 117, 125, 0.1)',
    label: entityType,
  };

  const sizes = {
    small: 18,
    medium: 24,
    large: 32,
  };

  const iconWithStyle = React.cloneElement(current.icon, {
    style: {
      color: current.color,
      fontSize: sizes[size],
    },
  } as any);

  if (showLabel) {
    return (
      <Box
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 1,
          px: 1.5,
          py: 0.5,
          borderRadius: '16px',
          backgroundColor: current.bg,
          color: current.color,
          fontWeight: 500,
          fontSize: '0.875rem',
        }}
      >
        {iconWithStyle}
        <span>{current.label}</span>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: sizes[size] + 8,
        height: sizes[size] + 8,
        borderRadius: '50%',
        backgroundColor: current.bg,
      }}
    >
      {iconWithStyle}
    </Box>
  );
};

export default PiiEntityIcon;
