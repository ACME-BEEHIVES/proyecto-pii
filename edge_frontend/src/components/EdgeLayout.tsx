import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';
import Tooltip from '@mui/material/Tooltip';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

// Icons
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SearchIcon from '@mui/icons-material/Search';
import SettingsIcon from '@mui/icons-material/Settings';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import SecurityIcon from '@mui/icons-material/Security';
import ShieldIcon from '@mui/icons-material/Shield';
import HubIcon from '@mui/icons-material/Hub';
import HelpIcon from '@mui/icons-material/Help';

import ServiceHealth from './ServiceHealth';

const drawerWidth = 280;

interface EdgeLayoutProps {
  children: React.ReactNode;
}

const EdgeLayout: React.FC<EdgeLayoutProps> = ({ children }) => {
  const [open, setOpen] = useState(true);
  const [profileAnchor, setProfileAnchor] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();
  const location = useLocation();

  const handleToggleDrawer = () => {
    setOpen(!open);
  };

  const handleProfileOpen = (event: React.MouseEvent<HTMLElement>) => {
    setProfileAnchor(event.currentTarget);
  };

  const handleProfileClose = () => {
    setProfileAnchor(null);
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Hallazgos PII', icon: <SearchIcon />, path: '/findings' },
    { text: 'Configuración', icon: <SettingsIcon />, path: '/config' },
    { text: 'Derechos ARCO (DSAR)', icon: <FingerprintIcon />, path: '/dsar' },
    { text: 'Censura de Archivos', icon: <SecurityIcon />, path: '/redaction' },
    { text: 'Gráfico de Identidad', icon: <HubIcon />, path: '/identity' },
    { text: 'divider', icon: null, path: '' },
    { text: 'Centro de Ayuda', icon: <HelpIcon />, path: '/help' },
  ];

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: '#F5F5F5' }}>
      {/* Header (AppBar) */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          width: '100%',
          backgroundColor: '#FFFFFF',
          color: '#343A40',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
          borderBottom: '1px solid #E9ECEF',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              onClick={handleToggleDrawer}
              edge="start"
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Box
              component="img"
              src="/logo_light.svg"
              alt="upshield Logo"
              sx={{
                height: 28,
                width: 'auto',
                display: 'block'
              }}
            />
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
              <Box component="span" sx={{ fontWeight: 400, color: 'text.secondary' }}>Edge Agent</Box>
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" sx={{ color: 'text.secondary', display: { xs: 'none', sm: 'block' }, mr: 1 }}>
              Administrador Edge
            </Typography>
            <Tooltip title="Perfil de Usuario">
              <IconButton onClick={handleProfileOpen} sx={{ p: 0 }}>
                <Avatar sx={{ bgcolor: 'primary.main', width: 36, height: 36, fontSize: '0.95rem', fontWeight: 600 }}>
                  AD
                </Avatar>
              </IconButton>
            </Tooltip>
            <Menu
              anchorEl={profileAnchor}
              open={Boolean(profileAnchor)}
              onClose={handleProfileClose}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <MenuItem onClick={handleProfileClose}>Mi Cuenta</MenuItem>
              <MenuItem onClick={handleProfileClose}>Configurar Llave PII</MenuItem>
              <Divider />
              <MenuItem onClick={handleProfileClose}>Cerrar Sesión</MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Sidebar (Drawer) */}
      <Drawer
        variant="permanent"
        open={open}
        sx={{
          width: open ? drawerWidth : 64,
          flexShrink: 0,
          whiteSpace: 'nowrap',
          boxSizing: 'border-box',
          '& .MuiDrawer-paper': {
            width: open ? drawerWidth : 64,
            transition: (theme) =>
              theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
            overflowX: 'hidden',
            backgroundColor: '#343A40',
            color: '#CED4DA',
            borderRight: 'none',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
          },
        }}
      >
        <Box>
          <Toolbar /> {/* Spacer below AppBar */}
          <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />
          
          <List sx={{ pt: 2 }}>
            {menuItems.map((item, index) => {
              if (item.text === 'divider') {
                return <Divider key={`divider-${index}`} sx={{ my: 1.5, borderColor: 'rgba(255,255,255,0.08)' }} />;
              }
              const isSelected = location.pathname === item.path;
              return (
                <ListItem key={item.text} disablePadding sx={{ display: 'block' }}>
                  <Tooltip title={!open ? item.text : ''} placement="right" arrow>
                    <ListItemButton
                      selected={isSelected}
                      onClick={() => navigate(item.path)}
                      sx={{
                        minHeight: 48,
                        justifyContent: open ? 'initial' : 'center',
                        px: 2.5,
                        py: 1.25,
                      }}
                    >
                      <ListItemIcon
                        sx={{
                          minWidth: 0,
                          mr: open ? 2 : 'auto',
                          justifyContent: 'center',
                        }}
                      >
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.text}
                        sx={{
                          opacity: open ? 1 : 0,
                          '& .MuiTypography-root': {
                            fontSize: '0.9rem',
                            fontWeight: isSelected ? 600 : 500,
                          },
                        }}
                      />
                    </ListItemButton>
                  </Tooltip>
                </ListItem>
              );
            })}
          </List>
        </Box>

        {/* Bottom Services Health Check Dashboard & Footer */}
        <Box>
          {open ? (
            <Box>
              <ServiceHealth />
              <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)', my: 1 }} />
              <Box sx={{ pb: 2, textAlign: 'center', opacity: 0.5 }}>
                <Typography variant="caption" sx={{ color: '#CED4DA', fontSize: '0.7rem' }}>
                  Powered by upshield
                </Typography>
              </Box>
            </Box>
          ) : (
            <Box sx={{ textAlign: 'center', pb: 2 }}>
              <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)', mb: 2 }} />
              <Tooltip title="Ver Estado de Servicios" placement="right" arrow>
                <IconButton onClick={() => setOpen(true)} size="small" sx={{ color: '#CED4DA' }}>
                  <ShieldIcon sx={{ color: '#28A745', fontSize: 20 }} />
                </IconButton>
              </Tooltip>
            </Box>
          )}
        </Box>
      </Drawer>

      {/* Main Content Pane */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          px: { xs: 2, md: 4 },
          py: 3,
          mt: '64px',
          backgroundColor: '#F8F9FA',
          minHeight: '100vh',
          width: '100%',
          overflowX: 'auto',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default EdgeLayout;
