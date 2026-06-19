import { createTheme } from '@mui/material/styles';

/**
 * Tema MUI del UpShield Edge Agent.
 * Basado en el tema de UpShield Final para consistencia visual.
 * Referencia: docs/UI_GUIDE_V1.md
 */
const theme = createTheme({
  palette: {
    primary: {
      main: '#007BFF', // Azul Principal
      dark: '#0056B3', // Azul Hover
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#6C757D', // Gris Medio
    },
    error: {
      main: '#DC3545', // Rojo — Riesgo ALTO / Datos sensibles
    },
    warning: {
      main: '#FFC107', // Amarillo — Riesgo MODERADO / Datos básicos
    },
    success: {
      main: '#28A745', // Verde — Sin hallazgos / Servicios OK
    },
    info: {
      main: '#17A2B8', // Cyan — Información
    },
    text: {
      primary: '#343A40', // Gris Oscuro
      secondary: '#6C757D', // Gris Medio
    },
    background: {
      default: '#F8F9FA', // Fondo general
      paper: '#FFFFFF', // Cards, modales
    },
    divider: '#E9ECEF', // Bordes, separadores
  },
  typography: {
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
    h1: {
      fontSize: '2.25rem',
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: '1.75rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h5: {
      fontSize: '1.1rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    caption: {
      fontSize: '0.75rem',
      color: '#6C757D',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          textTransform: 'none',
          fontWeight: 500,
          padding: '8px 20px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          },
          '&.MuiButton-containedPrimary': {
            '&:hover': {
              backgroundColor: '#0056B3',
            },
          },
          '&.MuiButton-outlinedPrimary': {
            borderColor: '#007BFF',
            color: '#007BFF',
            '&:hover': {
              backgroundColor: 'rgba(0, 123, 255, 0.04)',
            },
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 6,
            '& fieldset': {
              borderColor: '#E9ECEF',
            },
            '&:hover fieldset': {
              borderColor: '#BDBDBD',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#007BFF',
            },
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)',
          border: '1px solid #E9ECEF',
          '&:hover': {
            boxShadow: '0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
          borderRadius: 6,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          color: '#343A40',
          boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
          borderBottom: '1px solid #E9ECEF',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#343A40',
          color: '#CED4DA',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          marginLeft: 8,
          marginRight: 8,
          marginBottom: 4,
          '&.Mui-selected': {
            backgroundColor: '#007BFF',
            color: '#FFFFFF',
            '&:hover': {
              backgroundColor: '#007BFF',
            },
            '& .MuiListItemIcon-root': {
              color: '#FFFFFF',
            },
          },
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
          },
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          color: '#CED4DA',
          minWidth: 40,
        },
      },
    },
  },
});

export default theme;
