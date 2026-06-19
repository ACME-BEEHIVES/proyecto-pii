import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Slider from '@mui/material/Slider';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormGroup from '@mui/material/FormGroup';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import IconButton from '@mui/material/IconButton';
import Grid from '@mui/material/Grid';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import InputAdornment from '@mui/material/InputAdornment';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Switch from '@mui/material/Switch';
import Divider from '@mui/material/Divider';

// Icons
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import SettingsIcon from '@mui/icons-material/Settings';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import FolderIcon from '@mui/icons-material/Folder';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import StorageIcon from '@mui/icons-material/Storage';
import CloudIcon from '@mui/icons-material/Cloud';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import CheckIcon from '@mui/icons-material/Check';
import EmailIcon from '@mui/icons-material/Email';

import { api } from '../services/api';
import type { ScanConfig, DbConfig, DbConfigCreate } from '../types';

const ScanConfigPage: React.FC = () => {
  const [config, setConfig] = useState<ScanConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [newPath, setNewPath] = useState('');
  const [testResult, setTestResult] = useState<{ path: string; status: 'ok' | 'error'; message?: string } | null>(null);
  const [testingPath, setTestingPath] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // DB Config State
  const [dbConfigs, setDbConfigs] = useState<DbConfig[]>([]);
  const [selectedDbConfig, setSelectedDbConfig] = useState<DbConfig | null>(null);
  const [dbDialogOpen, setDbDialogOpen] = useState(false);
  const [dbForm, setDbForm] = useState<DbConfigCreate>({
    name: '',
    db_type: 'mysql',
    connection_string: '',
    tables_to_scan: {},
    is_active: true,
  });
  const [dbFormErrors, setDbFormErrors] = useState<Record<string, string>>({});
  const [dbTestResult, setDbTestResult] = useState<{ status: 'ok' | 'error'; message: string } | null>(null);
  const [dbTesting, setDbTesting] = useState(false);
  const [tablesJsonText, setTablesJsonText] = useState('');

  // Wizard States
  const [activeStep, setActiveStep] = useState(0);
  const [customConnStringMode, setCustomConnStringMode] = useState(false);
  const [dbHost, setDbHost] = useState('');
  const [dbPort, setDbPort] = useState<number | ''>('');
  const [dbUser, setDbUser] = useState('');
  const [dbPassword, setDbPassword] = useState('');
  const [dbDatabase, setDbDatabase] = useState('');
  const [availableSchema, setAvailableSchema] = useState<Record<string, string[]>>({});
  const [schemaLoading, setSchemaLoading] = useState(false);
  const [schemaError, setSchemaError] = useState<string | null>(null);
  const [showAdvancedJson, setShowAdvancedJson] = useState(false);

  const [browserOpen, setBrowserOpen] = useState(false);
  const [browserData, setBrowserData] = useState<{ current_path: string; parent_path: string | null; directories: string[] } | null>(null);
  const [browserLoading, setBrowserLoading] = useState(false);

  const handleOpenBrowser = async (path?: string) => {
    setBrowserOpen(true);
    setBrowserLoading(true);
    try {
      const res = await api.browseDir(path);
      setBrowserData(res);
    } catch (e) {
      console.error('Error browsing dir', e);
      alert('No se pudo abrir el directorio. Verifique los permisos o si el agente está corriendo.');
    } finally {
      setBrowserLoading(false);
    }
  };

  const handleNavigateBrowser = (path: string) => {
    handleOpenBrowser(path);
  };

  const handleSelectBrowserPath = () => {
    if (browserData) {
      setNewPath(browserData.current_path);
      setBrowserOpen(false);
    }
  };

  const loadDbConfigs = async () => {
    try {
      const data = await api.getDbConfigs();
      setDbConfigs(data);
    } catch (e) {
      console.error('Error loading DB configs', e);
    }
  };

  const loadConfig = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      const data = await api.getConfig();
      setConfig(data);
      await loadDbConfigs();
    } catch (e) {
      console.error('Error loading config', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfig(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAddPath = () => {
    if (!newPath.trim() || !config) return;
    if (config.scan_paths.includes(newPath.trim())) {
      alert('Esta ruta ya está agregada');
      return;
    }
    setConfig({
      ...config,
      scan_paths: [...config.scan_paths, newPath.trim()],
    });
    setNewPath('');
  };

  const handleRemovePath = (index: number) => {
    if (!config) return;
    const paths = [...config.scan_paths];
    paths.splice(index, 1);
    setConfig({ ...config, scan_paths: paths });
  };

  const handleTestPath = async (path: string) => {
    try {
      setTestingPath(path);
      setTestResult(null);
      const res = await api.testPath(path);
      setTestResult({ path, status: res.status, message: res.message });
    } catch {
      setTestResult({ path, status: 'error', message: 'Error de comunicación con el agente local' });
    } finally {
      setTestingPath(null);
    }
  };

  const handleToggleExtension = (ext: string) => {
    if (!config) return;
    const extensions = [...config.extensions];
    const idx = extensions.indexOf(ext);
    if (idx > -1) {
      extensions.splice(idx, 1);
    } else {
      extensions.push(ext);
    }
    setConfig({ ...config, extensions });
  };

  const handleToggleEntity = (entity: string) => {
    if (!config) return;
    const entities = [...config.entities];
    const idx = entities.indexOf(entity);
    if (idx > -1) {
      entities.splice(idx, 1);
    } else {
      entities.push(entity);
    }
    setConfig({ ...config, entities });
  };

  const handleSave = async () => {
    if (!config) return;
    try {
      setSuccessMsg(null);
      const updated = await api.updateConfig(config);
      setConfig(updated);
      setSuccessMsg('Configuración guardada exitosamente');
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (e: any) {
      console.error('Error saving config', e);
      alert(e.response?.data?.detail || 'No se pudo guardar la configuración');
    }
  };

  // DB Config Handlers
  const handleOpenDbDialog = (dbConfig?: DbConfig) => {
    setActiveStep(0);
    setSchemaError(null);
    setAvailableSchema({});
    setShowAdvancedJson(false);
    
    if (dbConfig) {
      setSelectedDbConfig(dbConfig);
      setDbForm({
        name: dbConfig.name,
        db_type: dbConfig.db_type,
        connection_string: '', 
        tables_to_scan: dbConfig.tables_to_scan,
        is_active: dbConfig.is_active,
      });
      setDbHost('');
      setDbPort('');
      setDbUser('');
      setDbPassword('');
      setDbDatabase('');
      setCustomConnStringMode(true);
      setTablesJsonText(JSON.stringify(dbConfig.tables_to_scan, null, 2));
    } else {
      setSelectedDbConfig(null);
      setDbForm({
        name: '',
        db_type: 'mysql',
        connection_string: '',
        tables_to_scan: {},
        is_active: true,
      });
      setDbHost('127.0.0.1');
      setDbPort(3306);
      setDbUser('root');
      setDbPassword('');
      setDbDatabase('');
      setCustomConnStringMode(false);
      setTablesJsonText('{}');
    }
    setDbTestResult(null);
    setDbFormErrors({});
    setDbDialogOpen(true);
  };

  const getConnPayload = () => {
    if (customConnStringMode) {
      return {
        db_type: dbForm.db_type,
        connection_string: dbForm.connection_string,
      };
    } else {
      return {
        db_type: dbForm.db_type,
        host: dbHost,
        port: dbPort ? Number(dbPort) : undefined,
        user: dbUser,
        password: dbPassword,
        database: dbDatabase,
      };
    }
  };

  const handleTestDbConnection = async () => {
    setDbTesting(true);
    setDbTestResult(null);
    try {
      const payload = getConnPayload();
      const res = await api.testDbConnection(payload as any);
      setDbTestResult(res);
      if (res.status === 'ok' && res.connection_string) {
        setDbForm((prev) => ({ ...prev, connection_string: res.connection_string! }));
      }
      return res.status === 'ok';
    } catch (e: any) {
      const msg = e.response?.data?.detail || 'Error al conectar con el servidor backend';
      setDbTestResult({
        status: 'error',
        message: msg,
      });
      return false;
    } finally {
      setDbTesting(false);
    }
  };

  const handleDbTypeChange = (dbType: 'mysql' | 'postgresql' | 'mssql') => {
    setDbForm({ ...dbForm, db_type: dbType });
    if (!customConnStringMode) {
      if (dbType === 'mysql') setDbPort(3306);
      else if (dbType === 'postgresql') setDbPort(5432);
      else if (dbType === 'mssql') setDbPort(1433);
    }
  };

  const handleProceedToSchema = async () => {
    const errors: Record<string, string> = {};
    if (!dbForm.name.trim()) {
      errors.name = 'El nombre de la conexión es requerido';
    }
    
    if (customConnStringMode) {
      if (!selectedDbConfig && !dbForm.connection_string.trim()) {
        errors.connection_string = 'La cadena de conexión es requerida';
      }
    } else {
      if (!dbHost.trim()) errors.host = 'El host es requerido';
      if (!dbUser.trim()) errors.user = 'El usuario es requerido';
      if (!dbDatabase.trim()) errors.database = 'La base de datos es requerida';
    }

    if (Object.keys(errors).length > 0) {
      setDbFormErrors(errors);
      return;
    }
    setDbFormErrors({});
    
    setSchemaLoading(true);
    setSchemaError(null);
    try {
      let res: { status: 'ok' | 'error'; tables: Record<string, string[]>; connection_string?: string };
      const isConnectionDetailsUntouched = selectedDbConfig && 
        customConnStringMode && 
        !dbForm.connection_string.trim();
        
      if (isConnectionDetailsUntouched) {
        res = await api.discoverDbSchemaExisting(selectedDbConfig.id);
      } else {
        const payload = getConnPayload();
        res = await api.discoverDbSchema(payload as any);
        if (res.connection_string) {
          setDbForm((prev) => ({ ...prev, connection_string: res.connection_string || '' }));
        }
      }
      
      if (res.status === 'ok') {
        setAvailableSchema(res.tables);
        if (Object.keys(res.tables).length === 0) {
          setSchemaError('No se encontraron tablas o columnas de tipo texto en esta base de datos.');
        } else {
          setActiveStep(1);
        }
      }
    } catch (e: any) {
      console.error(e);
      setSchemaError(e.response?.data?.detail || 'Error al conectar u obtener el esquema de tablas.');
    } finally {
      setSchemaLoading(false);
    }
  };

  const handleToggleColumn = (tableName: string, columnName: string) => {
    const currentTables = { ...dbForm.tables_to_scan };
    const cols = currentTables[tableName] ? [...currentTables[tableName]] : [];
    const idx = cols.indexOf(columnName);
    
    if (idx > -1) {
      cols.splice(idx, 1);
    } else {
      cols.push(columnName);
    }
    
    if (cols.length === 0) {
      delete currentTables[tableName];
    } else {
      currentTables[tableName] = cols;
    }
    
    setDbForm({ ...dbForm, tables_to_scan: currentTables });
    setTablesJsonText(JSON.stringify(currentTables, null, 2));
  };

  const handleToggleTableAll = (tableName: string, columns: string[], isSelected: boolean) => {
    const currentTables = { ...dbForm.tables_to_scan };
    if (isSelected) {
      delete currentTables[tableName];
    } else {
      currentTables[tableName] = [...columns];
    }
    setDbForm({ ...dbForm, tables_to_scan: currentTables });
    setTablesJsonText(JSON.stringify(currentTables, null, 2));
  };

  const handleSaveDbConfig = async () => {
    let finalTables = dbForm.tables_to_scan;
    if (showAdvancedJson) {
      try {
        finalTables = JSON.parse(tablesJsonText);
      } catch {
        setDbFormErrors({ tables_to_scan: 'Formato JSON inválido.' });
        return;
      }
    }
    
    if (Object.keys(finalTables).length === 0) {
      alert('Debe seleccionar al menos una columna para escanear.');
      return;
    }

    const payload = {
      ...dbForm,
      tables_to_scan: finalTables,
    };

    try {
      if (selectedDbConfig) {
        const updatePayload: Partial<DbConfigCreate> = { ...payload };
        if (!updatePayload.connection_string) {
          delete updatePayload.connection_string;
        }
        await api.updateDbConfig(selectedDbConfig.id, updatePayload);
        setSuccessMsg('Conexión de BD actualizada exitosamente');
      } else {
        if (!payload.connection_string) {
          setDbFormErrors({ connection_string: 'Debe probar la conexión exitosamente antes de guardar.' });
          return;
        }
        await api.createDbConfig(payload);
        setSuccessMsg('Conexión de BD creada exitosamente');
      }
      setDbDialogOpen(false);
      loadDbConfigs();
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Error al guardar la conexión de base de datos.');
    }
  };

  const handleDeleteDbConfig = async (id: number) => {
    if (!confirm('¿Está seguro de eliminar esta conexión a base de datos?')) return;
    try {
      await api.deleteDbConfig(id);
      loadDbConfigs();
      setSuccessMsg('Conexión de BD eliminada exitosamente');
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Error al eliminar la conexión.');
    }
  };

  const handleRunDbScan = async (id: number) => {
    try {
      await api.runDbScan(id);
      alert('Escaneo de base de datos iniciado en segundo plano.');
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Error al iniciar el escaneo de base de datos.');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  const allExtensions = ['.pdf', '.docx', '.xlsx', '.xls', '.doc', '.txt', '.jpg', '.png', '.csv'];
  const allEntities = [
    { value: 'CHILE_RUT', label: 'RUT (Chile)' },
    { value: 'EMAIL_ADDRESS', label: 'Correo Electrónico' },
    { value: 'PERSON', label: 'Nombre Persona' },
    { value: 'PHONE_NUMBER', label: 'Número de Teléfono' },
    { value: 'DATE_TIME', label: 'Fecha / Fecha de Nacimiento' },
    { value: 'DOMICILIO', label: 'Domicilio / Dirección' },
    { value: 'NACIONALIDAD', label: 'Nacionalidad / Gentilicio' },
    { value: 'PASAPORTE', label: 'Número de Pasaporte' },
    { value: 'LICENCIA_CONDUCIR', label: 'Licencia de Conducir' },
    { value: 'CUENTA_BANCARIA', label: 'Cuenta Bancaria / Tarjeta de Crédito' },
    { value: 'NUMERO_SERIE_DOC', label: 'N° Serie / Folio de Documento' },
    { value: 'DATA_SALUD', label: 'Datos de Salud (Sensible)' },
    { value: 'DATA_ETNIA', label: 'Pertenencia Etnia (Sensible)' },
    { value: 'DATA_POLITICA', label: 'Afiliación Política (Sensible)' },
    { value: 'DATA_RELIGION', label: 'Creencia Religiosa (Sensible)' },
    { value: 'DATA_SEXUALIDAD', label: 'Identidad/Orientación Sexual (Sensible)' },
    { value: 'DATA_SINDICAL', label: 'Afiliación Sindical (Sensible)' },
    { value: 'DATA_SOCIOECONOMICO', label: 'Estado Socioeconómico (Sensible)' },
    { value: 'DATA_IDEOLOGIA', label: 'Convicciones Ideológicas/Filosóficas (Sensible)' },
    { value: 'DATA_BIOLOGICO', label: 'Perfil Biológico Humano (Sensible)' },
    { value: 'DATA_BIOMETRICO', label: 'Datos Biométricos (Sensible)' },
    { value: 'DATA_PENAL', label: 'Antecedentes Penales (Sensible)' },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
            Configuración del Escaneo
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Modifica parámetros, rutas de red locales, formatos de archivos y entidades de interés
          </Typography>
        </Box>
      </Box>

      {successMsg && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {successMsg}
        </Alert>
      )}

      {config && (
        <Grid container spacing={3}>
          {/* Left panel: Paths & MySQL Database */}
          <Grid size={{ xs: 12, md: 7 }}>
            <Card>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 700 }} gutterBottom>
                  Rutas de Red a Escanear
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Agrega rutas completas de red o carpetas locales. El agente rechazará carpetas críticas del sistema (ej. C:\Windows).
                </Typography>

                <Box sx={{ display: 'flex', gap: 1.5, mb: 3 }}>
                  <TextField
                    label="Nueva Ruta de Directorio"
                    variant="outlined"
                    fullWidth
                    size="small"
                    placeholder="Ej. C:\Users\Admin\Documents o \\server\shared"
                    value={newPath}
                    onChange={(e) => setNewPath(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddPath()}
                    slotProps={{
                      input: {
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton onClick={() => handleOpenBrowser(newPath || undefined)} edge="end" title="Examinar carpetas localmente">
                              <FolderOpenIcon />
                            </IconButton>
                          </InputAdornment>
                        )
                      }
                    }}
                  />
                  <Button variant="contained" onClick={handleAddPath} startIcon={<AddIcon />}>
                    Agregar
                  </Button>
                </Box>

                <List sx={{ border: '1px solid #E9ECEF', borderRadius: '6px', p: 0, maxHeight: 350, overflowY: 'auto' }}>
                  {config.scan_paths.length > 0 ? (
                    config.scan_paths.map((path, idx) => (
                      <ListItem
                        key={idx}
                        secondaryAction={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Button
                              variant="outlined"
                              size="small"
                              disabled={testingPath !== null}
                              onClick={() => handleTestPath(path)}
                            >
                              {testingPath === path ? <CircularProgress size={16} /> : 'Probar'}
                            </Button>
                            <IconButton edge="end" aria-label="delete" onClick={() => handleRemovePath(idx)}>
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        }
                        sx={{
                          borderBottom: idx < config.scan_paths.length - 1 ? '1px solid #E9ECEF' : 'none',
                          '&:hover': { backgroundColor: 'rgba(0,0,0,0.01)' },
                        }}
                      >
                        <ListItemText
                          primary={path}
                          sx={{ '& .MuiTypography-root': { fontSize: '0.9rem', pr: 14 } }}
                        />
                      </ListItem>
                    ))
                  ) : (
                    <ListItem sx={{ py: 3, justifyContent: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        No hay rutas configuradas. Agrega una arriba.
                      </Typography>
                    </ListItem>
                  )}
                </List>

                {/* Path Connection Test Results */}
                {testResult && (
                  <Alert
                    severity={testResult.status === 'ok' ? 'success' : 'error'}
                    sx={{ mt: 2 }}
                    icon={testResult.status === 'ok' ? <CheckCircleIcon /> : <ErrorIcon />}
                  >
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      {testResult.status === 'ok' ? 'Ruta Accesible' : 'Error de Acceso'}
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                      <strong>Directorio:</strong> {testResult.path}
                    </Typography>
                    {testResult.message && (
                      <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                        {testResult.message}
                      </Typography>
                    )}
                  </Alert>
                )}
              </CardContent>
            </Card>

            {/* Conectores de Base de Datos SQL Card */}
            <Card sx={{ mt: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <StorageIcon color="primary" /> Conectores de Base de Datos SQL
                  </Typography>
                  <Button 
                    variant="contained" 
                    size="small" 
                    startIcon={<AddIcon />}
                    onClick={() => handleOpenDbDialog()}
                  >
                    Nueva Conexión SQL
                  </Button>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Configura bases de datos externas (MySQL, PostgreSQL, SQL Server) para escanear sus tablas y columnas estructuradas en busca de PII.
                </Typography>

                <List sx={{ border: '1px solid #E9ECEF', borderRadius: '6px', p: 0 }}>
                  {dbConfigs.length > 0 ? (
                    dbConfigs.map((dbC, idx) => (
                      <ListItem
                        key={dbC.id}
                        secondaryAction={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Button
                              variant="outlined"
                              size="small"
                              color="primary"
                              onClick={() => handleRunDbScan(dbC.id)}
                            >
                              Escanear
                            </Button>
                            <Button
                              variant="outlined"
                              size="small"
                              color="secondary"
                              onClick={() => handleOpenDbDialog(dbC)}
                            >
                              Editar
                            </Button>
                            <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteDbConfig(dbC.id)}>
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        }
                        sx={{
                          borderBottom: idx < dbConfigs.length - 1 ? '1px solid #E9ECEF' : 'none',
                          '&:hover': { backgroundColor: 'rgba(0,0,0,0.01)' },
                        }}
                      >
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                {dbC.name}
                              </Typography>
                              <Box 
                                component="span" 
                                sx={{ 
                                  fontSize: '0.75rem', 
                                  bgcolor: 'primary.light', 
                                  color: 'primary.contrastText', 
                                  px: 1, 
                                  py: 0.25, 
                                  borderRadius: 1,
                                  textTransform: 'uppercase',
                                  fontWeight: 'bold'
                                }}
                              >
                                {dbC.db_type}
                              </Box>
                              {!dbC.is_active && (
                                <Box 
                                  component="span" 
                                  sx={{ 
                                    fontSize: '0.75rem', 
                                    bgcolor: 'grey.300', 
                                    color: 'text.secondary', 
                                    px: 1, 
                                    py: 0.25, 
                                    borderRadius: 1,
                                    fontWeight: 'bold'
                                  }}
                                >
                                  Inactivo
                                </Box>
                              )}
                            </Box>
                          }
                          secondary={
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                              <strong>Tablas:</strong> {Object.keys(dbC.tables_to_scan).join(', ') || 'Ninguna'}
                            </Typography>
                          }
                        />
                      </ListItem>
                    ))
                  ) : (
                    <ListItem sx={{ py: 3, justifyContent: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        No hay bases de datos externas configuradas. Agrega una arriba.
                      </Typography>
                    </ListItem>
                  )}
                </List>
              </CardContent>
            </Card>

            {/* Base de Datos MySQL Card */}
            <Card sx={{ mt: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }} gutterBottom>
                  <StorageIcon color="primary" /> Conexión a Base de Datos MySQL
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Modifica los parámetros de conexión de la base de datos local. El agente validará la conexión al guardar.
                </Typography>

                <Grid container spacing={2}>
                  <Grid size={{ xs: 12, sm: 8 }}>
                    <TextField
                      label="Servidor / Host"
                      variant="outlined"
                      fullWidth
                      size="small"
                      value={config.db_host || ''}
                      onChange={(e) => setConfig({ ...config, db_host: e.target.value })}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <TextField
                      label="Puerto"
                      variant="outlined"
                      fullWidth
                      size="small"
                      value={config.db_port || ''}
                      onChange={(e) => setConfig({ ...config, db_port: e.target.value })}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Usuario"
                      variant="outlined"
                      fullWidth
                      size="small"
                      value={config.db_user || ''}
                      onChange={(e) => setConfig({ ...config, db_user: e.target.value })}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Contraseña"
                      type="password"
                      variant="outlined"
                      fullWidth
                      size="small"
                      value={config.db_password || ''}
                      onChange={(e) => setConfig({ ...config, db_password: e.target.value })}
                    />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <TextField
                      label="Nombre de Base de Datos"
                      variant="outlined"
                      fullWidth
                      size="small"
                      value={config.db_name || ''}
                      onChange={(e) => setConfig({ ...config, db_name: e.target.value })}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Credenciales de UpShield Cloud Card */}
            <Card sx={{ mt: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }} gutterBottom>
                  <CloudIcon color="primary" /> Conexión a UpShield Cloud (Plataforma Central)
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Configura las credenciales del agente para reportar hallazgos consolidados y estadísticas a la consola central.
                </Typography>

                <Grid container spacing={2}>
                  <Grid size={{ xs: 12 }}>
                    <TextField
                      label="URL de la API de UpShield"
                      variant="outlined"
                      fullWidth
                      size="small"
                      value={config.upshield_api_url || ''}
                      onChange={(e) => setConfig({ ...config, upshield_api_url: e.target.value })}
                      placeholder="Ej. https://app.upshield.cl/api"
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 8 }}>
                    <TextField
                      label="API Key (Token de Acceso)"
                      variant="outlined"
                      fullWidth
                      size="small"
                      type="password"
                      value={config.upshield_api_key || ''}
                      onChange={(e) => setConfig({ ...config, upshield_api_key: e.target.value })}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <TextField
                      label="Intervalo Sinc. (s)"
                      variant="outlined"
                      fullWidth
                      size="small"
                      type="number"
                      value={config.upshield_sync_interval ?? 60}
                      onChange={(e) => setConfig({ ...config, upshield_sync_interval: Number(e.target.value) })}
                    />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <TextField
                      label="ID de Organización / Tenant ID"
                      variant="outlined"
                      fullWidth
                      size="small"
                      value={config.upshield_tenant_id || ''}
                      onChange={(e) => setConfig({ ...config, upshield_tenant_id: e.target.value })}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Alertas por Correo (SMTP) Card */}
            <Card sx={{ mt: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <EmailIcon color="primary" /> Alertas por Correo Electrónico (SMTP)
                  </Typography>
                  <Switch
                    checked={config.alert_emails_enabled || false}
                    onChange={(e) => setConfig({ ...config, alert_emails_enabled: e.target.checked })}
                    color="primary"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Recibe notificaciones automáticas al correo del administrador en caso de que algún servicio de Docker (base de datos, Tika, Presidio o Watcher) deje de funcionar.
                </Typography>

                {config.alert_emails_enabled && (
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, sm: 8 }}>
                      <TextField
                        label="Servidor SMTP (Host)"
                        variant="outlined"
                        fullWidth
                        size="small"
                        value={config.smtp_host || ''}
                        onChange={(e) => setConfig({ ...config, smtp_host: e.target.value })}
                        placeholder="Ej. smtp.gmail.com o localhost"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, sm: 4 }}>
                      <TextField
                        label="Puerto"
                        variant="outlined"
                        fullWidth
                        size="small"
                        type="number"
                        value={config.smtp_port ?? 587}
                        onChange={(e) => setConfig({ ...config, smtp_port: Number(e.target.value) })}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6 }}>
                      <TextField
                        label="Usuario SMTP"
                        variant="outlined"
                        fullWidth
                        size="small"
                        value={config.smtp_username || ''}
                        onChange={(e) => setConfig({ ...config, smtp_username: e.target.value })}
                        placeholder="Ej. admin@miempresa.com"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6 }}>
                      <TextField
                        label="Contraseña SMTP"
                        variant="outlined"
                        fullWidth
                        size="small"
                        type="password"
                        value={config.smtp_password || ''}
                        onChange={(e) => setConfig({ ...config, smtp_password: e.target.value })}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6 }}>
                      <TextField
                        label="Remitente (De)"
                        variant="outlined"
                        fullWidth
                        size="small"
                        value={config.smtp_from || ''}
                        onChange={(e) => setConfig({ ...config, smtp_from: e.target.value })}
                        placeholder="Ej. alertas@upshield-edge.cl"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6 }}>
                      <TextField
                        label="Destinatario de Alertas (Para)"
                        variant="outlined"
                        fullWidth
                        size="small"
                        value={config.smtp_to || ''}
                        onChange={(e) => setConfig({ ...config, smtp_to: e.target.value })}
                        placeholder="Ej. admin@miempresa.com"
                        helperText="Para múltiples destinatarios, separar por comas."
                      />
                    </Grid>
                    <Grid size={{ xs: 12 }}>
                      <TextField
                        label="Intervalo de Chequeo (s)"
                        variant="outlined"
                        fullWidth
                        size="small"
                        type="number"
                        value={config.alert_check_interval ?? 60}
                        onChange={(e) => setConfig({ ...config, alert_check_interval: Number(e.target.value) })}
                        helperText="Frecuencia en segundos con la que se comprueba el estado de los servicios."
                      />
                    </Grid>
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Right panel: Workers, Extensions, Entities */}
          <Grid size={{ xs: 12, md: 5 }}>
            <Card sx={{ mb: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SettingsIcon /> Parámetros del Motor
                </Typography>

                <Box sx={{ mt: 2.5 }}>
                  <Typography id="workers-slider" variant="subtitle2" sx={{ fontWeight: 600 }} gutterBottom>
                    Hilos de ejecución (Workers): {config.max_workers}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                    Un mayor número acelera el procesamiento de OCR pero consume más CPU.
                  </Typography>
                  <Box sx={{ px: 1.5 }}>
                    <Slider
                      aria-labelledby="workers-slider"
                      value={config.max_workers}
                      min={1}
                      max={8}
                      step={1}
                      marks
                      valueLabelDisplay="auto"
                      onChange={(_, val) => setConfig({ ...config, max_workers: val as number })}
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>

            {/* Programación de Escaneo Card */}
            <Card sx={{ mb: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <AccessTimeIcon color="primary" /> Programación de Escaneo
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5 }}>
                  Define cuándo debe ejecutarse automáticamente el escaneo incremental de archivos.
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                  <FormControl fullWidth size="small">
                    <InputLabel id="schedule-type-label">Frecuencia de Escaneo</InputLabel>
                    <Select
                      labelId="schedule-type-label"
                      value={config.schedule_type || 'none'}
                      label="Frecuencia de Escaneo"
                      onChange={(e) => setConfig({ 
                        ...config, 
                        schedule_type: e.target.value as 'none' | 'hourly' | 'daily' | 'weekly'
                      })}
                    >
                      <MenuItem value="none">No programado (Manual)</MenuItem>
                      <MenuItem value="daily">Diario</MenuItem>
                      <MenuItem value="weekly">Semanal</MenuItem>
                    </Select>
                  </FormControl>

                  {config.schedule_type !== 'none' && (
                    <TextField
                      label="Hora de ejecución"
                      type="time"
                      fullWidth
                      size="small"
                      value={config.schedule_time || '00:00'}
                      onChange={(e) => setConfig({ ...config, schedule_time: e.target.value })}
                      slotProps={{
                        inputLabel: {
                          shrink: true,
                        }
                      }}
                    />
                  )}

                  {config.schedule_type === 'weekly' && (
                    <FormControl fullWidth size="small">
                      <InputLabel id="schedule-day-label">Día de la semana</InputLabel>
                      <Select
                        labelId="schedule-day-label"
                        value={config.schedule_day ?? 0}
                        label="Día de la semana"
                        onChange={(e) => setConfig({ ...config, schedule_day: Number(e.target.value) })}
                      >
                        <MenuItem value={0}>Lunes</MenuItem>
                        <MenuItem value={1}>Martes</MenuItem>
                        <MenuItem value={2}>Miércoles</MenuItem>
                        <MenuItem value={3}>Jueves</MenuItem>
                        <MenuItem value={4}>Viernes</MenuItem>
                        <MenuItem value={5}>Sábado</MenuItem>
                        <MenuItem value={6}>Domingo</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                </Box>
              </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 700 }} gutterBottom>
                  Formatos de Archivos
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                  Solo los archivos con estas extensiones serán examinados.
                </Typography>

                <FormGroup sx={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 1 }}>
                  {allExtensions.map((ext) => (
                    <FormControlLabel
                      key={ext}
                      control={
                        <Checkbox
                          checked={config.extensions.includes(ext)}
                          onChange={() => handleToggleExtension(ext)}
                        />
                      }
                      label={ext.toUpperCase()}
                      sx={{ '& .MuiFormControlLabel-label': { fontSize: '0.85rem' } }}
                    />
                  ))}
                </FormGroup>
              </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 700 }} gutterBottom>
                  Entidades a Detectar
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                  Categorías legales exigidas para cumplimiento Ley 21.719.
                </Typography>

                <FormGroup sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                  {allEntities.map((entity) => (
                    <FormControlLabel
                      key={entity.value}
                      control={
                        <Checkbox
                          checked={config.entities.includes(entity.value)}
                          onChange={() => handleToggleEntity(entity.value)}
                        />
                      }
                      label={entity.label}
                      sx={{ '& .MuiFormControlLabel-label': { fontSize: '0.85rem' } }}
                    />
                  ))}
                </FormGroup>
              </CardContent>
            </Card>

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mb: 4 }}>
              <Button variant="outlined" color="secondary" onClick={() => loadConfig()}>
                Reestablecer
              </Button>
              <Button variant="contained" color="primary" onClick={handleSave}>
                Guardar Configuración
              </Button>
            </Box>
          </Grid>
        </Grid>
      )}

      {/* Dialog para explorar carpetas localmente */}
      <Dialog open={browserOpen} onClose={() => setBrowserOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 700 }}>
          <FolderOpenIcon color="primary" /> Seleccionar Carpeta de Escaneo
        </DialogTitle>
        <DialogContent dividers sx={{ minHeight: 300, maxHeight: 450, p: 2 }}>
          {browserLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 250 }}>
              <CircularProgress size={32} />
            </Box>
          ) : (
            <Box>
              {/* Ruta Actual */}
              <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1, bgcolor: '#F8F9FA', p: 1.5, borderRadius: 1.5, border: '1px solid #E9ECEF' }}>
                <Typography variant="body2" sx={{ fontWeight: 600, wordBreak: 'break-all' }}>
                  Ruta actual: {browserData?.current_path}
                </Typography>
              </Box>

              <List sx={{ p: 0 }}>
                {/* Botón para subir nivel */}
                {browserData?.parent_path && (
                  <ListItemButton 
                    onClick={() => handleNavigateBrowser(browserData.parent_path!)}
                    sx={{ borderRadius: 1, mb: 0.5 }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <ArrowUpwardIcon color="action" />
                    </ListItemIcon>
                    <ListItemText>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>[Subir un nivel]</Typography>
                    </ListItemText>
                  </ListItemButton>
                )}

                {/* Subcarpetas */}
                {browserData && browserData.directories.length > 0 ? (
                  browserData.directories.map((dir) => {
                    const separator = browserData.current_path.includes('\\') ? '\\' : '/';
                    const pathSeparator = browserData.current_path.endsWith(separator) ? '' : separator;
                    const nextPath = `${browserData.current_path}${pathSeparator}${dir}`;

                    return (
                      <ListItemButton 
                        key={dir} 
                        onClick={() => handleNavigateBrowser(nextPath)}
                        sx={{ borderRadius: 1, mb: 0.5 }}
                      >
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <FolderIcon sx={{ color: '#FFC107' }} />
                        </ListItemIcon>
                        <ListItemText>
                          <Typography variant="body2">{dir}</Typography>
                        </ListItemText>
                      </ListItemButton>
                    );
                  })
                ) : (
                  <Box sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      No hay subcarpetas en este directorio.
                    </Typography>
                  </Box>
                )}
              </List>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button variant="outlined" color="secondary" onClick={() => setBrowserOpen(false)}>
            Cancelar
          </Button>
          <Button variant="contained" color="primary" onClick={handleSelectBrowserPath} disabled={!browserData}>
            Seleccionar esta carpeta
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog para agregar/editar conexiones a bases de datos relacionales */}
      <Dialog open={dbDialogOpen} onClose={() => setDbDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700, pb: 1 }}>
          {selectedDbConfig ? 'Editar Conexión SQL' : 'Nueva Conexión a Base de Datos SQL'}
        </DialogTitle>
        <DialogContent dividers sx={{ p: 3 }}>
          {/* Stepper para indicar progreso */}
          <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
            <Step>
              <StepLabel>Paso 1: Conexión</StepLabel>
            </Step>
            <Step>
              <StepLabel>Paso 2: Tablas y Columnas</StepLabel>
            </Step>
          </Stepper>

          {activeStep === 0 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
              <TextField
                label="Nombre de la Conexión"
                variant="outlined"
                fullWidth
                size="small"
                value={dbForm.name}
                onChange={(e) => setDbForm({ ...dbForm, name: e.target.value })}
                placeholder="Ej. Base de Producción o Clientes"
                error={!!dbFormErrors.name}
                helperText={dbFormErrors.name}
              />

              <FormControl fullWidth size="small">
                <InputLabel id="db-type-select-label">Tipo de Base de Datos</InputLabel>
                <Select
                  labelId="db-type-select-label"
                  value={dbForm.db_type}
                  label="Tipo de Base de Datos"
                  onChange={(e) => handleDbTypeChange(e.target.value as 'mysql' | 'postgresql' | 'mssql')}
                >
                  <MenuItem value="mysql">MySQL / MariaDB</MenuItem>
                  <MenuItem value="postgresql">PostgreSQL</MenuItem>
                  <MenuItem value="mssql">SQL Server (Microsoft)</MenuItem>
                </Select>
              </FormControl>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', my: 0.5 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Usar Cadena de Conexión personalizada (avanzado)
                </Typography>
                <Switch 
                  checked={customConnStringMode} 
                  onChange={(e) => setCustomConnStringMode(e.target.checked)} 
                  size="small"
                />
              </Box>

              {!customConnStringMode ? (
                <Grid container spacing={2}>
                  <Grid size={{ xs: 12, sm: 8 }}>
                    <TextField
                      label="Host / Servidor"
                      variant="outlined"
                      fullWidth
                      size="small"
                      value={dbHost}
                      onChange={(e) => setDbHost(e.target.value)}
                      placeholder="host.docker.internal o db.company.internal"
                      error={!!dbFormErrors.host}
                      helperText={dbFormErrors.host || "Nota: Usa host.docker.internal si tu base de datos está local en la máquina host."}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <TextField
                      label="Puerto"
                      variant="outlined"
                      fullWidth
                      size="small"
                      type="number"
                      value={dbPort}
                      onChange={(e) => setDbPort(e.target.value === '' ? '' : Number(e.target.value))}
                      error={!!dbFormErrors.port}
                      helperText={dbFormErrors.port}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Usuario"
                      variant="outlined"
                      fullWidth
                      size="small"
                      value={dbUser}
                      onChange={(e) => setDbUser(e.target.value)}
                      error={!!dbFormErrors.user}
                      helperText={dbFormErrors.user}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Contraseña"
                      variant="outlined"
                      fullWidth
                      size="small"
                      type="password"
                      value={dbPassword}
                      onChange={(e) => setDbPassword(e.target.value)}
                      placeholder={selectedDbConfig ? 'Sin cambios (dejar en blanco)' : 'Contraseña de la BD'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <TextField
                      label="Nombre de la Base de Datos"
                      variant="outlined"
                      fullWidth
                      size="small"
                      value={dbDatabase}
                      onChange={(e) => setDbDatabase(e.target.value)}
                      error={!!dbFormErrors.database}
                      helperText={dbFormErrors.database}
                    />
                  </Grid>
                </Grid>
              ) : (
                <TextField
                  label="Cadena de Conexión (Connection String)"
                  variant="outlined"
                  fullWidth
                  size="small"
                  type="password"
                  value={dbForm.connection_string}
                  onChange={(e) => setDbForm({ ...dbForm, connection_string: e.target.value })}
                  placeholder={
                    dbForm.db_type === 'mysql'
                      ? 'mysql+mysqlconnector://user:pass@host:port/dbname'
                      : dbForm.db_type === 'postgresql'
                      ? 'postgresql://user:pass@host:port/dbname'
                      : 'mssql+pymssql://user:pass@host:port/dbname'
                  }
                  error={!!dbFormErrors.connection_string}
                  helperText={dbFormErrors.connection_string || (selectedDbConfig ? 'Dejar en blanco para mantener la contraseña actual' : 'Nota: Usa host.docker.internal si tu base de datos está local en la máquina host.')}
                />
              )}

              {/* Test Connection Results */}
              {dbTestResult && (
                <Alert severity={dbTestResult.status === 'ok' ? 'success' : 'error'} sx={{ mt: 1 }}>
                  {dbTestResult.message}
                </Alert>
              )}
            </Box>
          )}

          {activeStep === 1 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2" sx={{ fontWeight: 700 }}>
                  Seleccionar Tablas y Columnas a Escanear:
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={showAdvancedJson}
                      onChange={(e) => setShowAdvancedJson(e.target.checked)}
                      size="small"
                    />
                  }
                  label="Edición JSON avanzada"
                  sx={{ '& .MuiFormControlLabel-label': { fontSize: '0.75rem', fontWeight: 600 } }}
                />
              </Box>

              {schemaError && (
                <Alert severity="warning">
                  {schemaError}
                </Alert>
              )}

              {showAdvancedJson ? (
                <TextField
                  label="Estructura a Escanear (JSON)"
                  variant="outlined"
                  fullWidth
                  multiline
                  rows={8}
                  value={tablesJsonText}
                  onChange={(e) => setTablesJsonText(e.target.value)}
                  placeholder='{\n  "nombre_tabla": ["columna1", "columna2"]\n}'
                  error={!!dbFormErrors.tables_to_scan}
                  helperText={dbFormErrors.tables_to_scan || 'Estructura JSON: {"tabla": ["columnas"]}'}
                />
              ) : (
                <Box sx={{ maxHeight: 350, overflowY: 'auto', border: '1px solid #E9ECEF', borderRadius: 1.5, p: 1, bgcolor: '#FAFBFD' }}>
                  {schemaLoading ? (
                    <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: 200, gap: 1.5 }}>
                      <CircularProgress size={32} />
                      <Typography variant="body2" color="text.secondary">Descubriendo esquema de base de datos...</Typography>
                    </Box>
                  ) : Object.keys(availableSchema).length > 0 ? (
                    Object.entries(availableSchema).map(([tableName, columns]) => {
                      const selectedCols = dbForm.tables_to_scan[tableName] || [];
                      const isPartiallySelected = selectedCols.length > 0 && selectedCols.length < columns.length;

                      return (
                        <Accordion key={tableName} variant="outlined" sx={{ mb: 1, border: '1px solid #E9ECEF', borderRadius: '6px !important', overflow: 'hidden', '&:before': { display: 'none' } }}>
                          <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ minHeight: 48, '& .MuiAccordionSummary-content': { my: 0 } }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 0.5 }}>
                              <Checkbox
                                size="small"
                                checked={selectedCols.length > 0}
                                indeterminate={isPartiallySelected}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleToggleTableAll(tableName, columns, selectedCols.length > 0);
                                }}
                              />
                              <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
                                {tableName}
                              </Typography>
                              <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto', mr: 2, fontWeight: 500 }}>
                                {selectedCols.length} / {columns.length} col.
                              </Typography>
                            </Box>
                          </AccordionSummary>
                          <AccordionDetails sx={{ p: 2, pt: 1, bgcolor: '#FFFFFF' }}>
                            <Divider sx={{ mb: 1.5 }} />
                            <FormGroup sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 0.5 }}>
                              {columns.map((col) => {
                                const isChecked = selectedCols.includes(col);
                                return (
                                  <FormControlLabel
                                    key={col}
                                    control={
                                      <Checkbox
                                        size="small"
                                        checked={isChecked}
                                        onChange={() => handleToggleColumn(tableName, col)}
                                      />
                                    }
                                    label={col}
                                    sx={{ '& .MuiFormControlLabel-label': { fontSize: '0.8rem', color: 'text.secondary' } }}
                                  />
                                );
                              })}
                            </FormGroup>
                          </AccordionDetails>
                        </Accordion>
                      );
                    })
                  ) : (
                    <Box sx={{ p: 3, textAlign: 'center' }}>
                      <Typography variant="body2" color="text.secondary">Haga clic en Siguiente para cargar las tablas de la base de datos.</Typography>
                    </Box>
                  )}
                </Box>
              )}

              <FormControlLabel
                control={
                  <Checkbox
                    checked={dbForm.is_active}
                    onChange={(e) => setDbForm({ ...dbForm, is_active: e.target.checked })}
                  />
                }
                label="Conexión Activa"
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1, px: 3 }}>
          {activeStep === 0 ? (
            <>
              <Button 
                variant="outlined" 
                color="primary" 
                disabled={dbTesting}
                onClick={handleTestDbConnection}
                size="small"
              >
                {dbTesting ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
                Probar Conexión
              </Button>
              <Box sx={{ flexGrow: 1 }} />
              <Button variant="outlined" color="secondary" onClick={() => setDbDialogOpen(false)} size="small">
                Cancelar
              </Button>
              <Button 
                variant="contained" 
                color="primary" 
                disabled={schemaLoading}
                onClick={handleProceedToSchema}
                endIcon={schemaLoading ? <CircularProgress size={16} /> : <NavigateNextIcon />}
                size="small"
              >
                Siguiente
              </Button>
            </>
          ) : (
            <>
              <Button 
                variant="outlined" 
                color="secondary"
                onClick={() => setActiveStep(0)}
                startIcon={<NavigateBeforeIcon />}
                size="small"
              >
                Atrás
              </Button>
              <Box sx={{ flexGrow: 1 }} />
              <Button variant="outlined" color="secondary" onClick={() => setDbDialogOpen(false)} size="small">
                Cancelar
              </Button>
              <Button 
                variant="contained" 
                color="primary" 
                onClick={handleSaveDbConfig}
                startIcon={<CheckIcon />}
                size="small"
              >
                Guardar
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ScanConfigPage;
