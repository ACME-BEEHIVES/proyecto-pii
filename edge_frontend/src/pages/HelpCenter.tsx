import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Paper from '@mui/material/Paper';
import Chip from '@mui/material/Chip';
import Alert from '@mui/material/Alert';
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import StepContent from '@mui/material/StepContent';
import Divider from '@mui/material/Divider';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';

// Icons
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
// SettingsIcon removed — unused
import SearchIcon from '@mui/icons-material/Search';
import SecurityIcon from '@mui/icons-material/Security';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import HubIcon from '@mui/icons-material/Hub';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import StorageIcon from '@mui/icons-material/Storage';
import FolderIcon from '@mui/icons-material/Folder';
import DashboardIcon from '@mui/icons-material/Dashboard';
import DescriptionIcon from '@mui/icons-material/Description';
import LockIcon from '@mui/icons-material/Lock';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import GavelIcon from '@mui/icons-material/Gavel';

// ---------------------------------------------------------------------------
// Shared styles
// ---------------------------------------------------------------------------

const accordionSx = {
  mb: 2,
  elevation: 0,
  border: '1px solid',
  borderColor: 'divider',
  borderLeft: '4px solid',
  borderLeftColor: 'primary.main',
  borderRadius: '8px !important',
  '&::before': { display: 'none' },
  '&.Mui-expanded': { margin: 0, mb: 2 },
};

const accordionSummarySx = {
  '& .MuiAccordionSummary-content': { alignItems: 'center', gap: 1.5 },
};

const sectionIconSx = (bgColor: string) => ({
  width: 36,
  height: 36,
  bgcolor: bgColor,
  color: '#FFFFFF',
  fontSize: 20,
});

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

const HelpCenter: React.FC = () => {
  const [expanded, setExpanded] = useState<string | false>(false);

  const handleChange = (panel: string) => (_: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded ? panel : false);
  };

  return (
    <Box sx={{ maxWidth: 960, mx: 'auto', py: 4, px: { xs: 2, md: 0 } }}>
      {/* ---------------------------------------------------------------- */}
      {/* Header                                                           */}
      {/* ---------------------------------------------------------------- */}
      <Paper
        elevation={0}
        sx={{
          p: 4,
          mb: 4,
          borderRadius: 2,
          border: '1px solid',
          borderColor: 'divider',
          background: 'linear-gradient(135deg, #007BFF 0%, #0056B3 100%)',
          color: '#FFFFFF',
        }}
      >
        <Typography variant="h4" sx={{ fontWeight: 700 }} gutterBottom>
          Centro de Ayuda
        </Typography>
        <Typography variant="body1" sx={{ opacity: 0.9, mb: 2 }}>
          Guía paso a paso para configurar y operar UpShield Edge Agent
        </Typography>
      </Paper>

      <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
        Esta herramienta cumple con los requisitos de la Ley 21.719 de Protección de Datos
        Personales de Chile.
      </Alert>

      {/* ================================================================ */}
      {/* SECTION 1 — ¿Qué es UpShield Edge Agent?                        */}
      {/* ================================================================ */}
      <Accordion
        expanded={expanded === 'panel1'}
        onChange={handleChange('panel1')}
        elevation={0}
        sx={accordionSx}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={accordionSummarySx}>
          <Avatar sx={sectionIconSx('#007BFF')}>
            <SecurityIcon fontSize="small" />
          </Avatar>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            ¿Qué es UpShield Edge Agent?
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body1" sx={{ mb: 2 }}>
            UpShield Edge Agent es una herramienta <strong>on-premise</strong> que opera dentro de la
            red de tu organización para descubrir datos personales (PII) en archivos y bases de
            datos, en cumplimiento con la <strong>Ley 21.719</strong> de Protección de Datos
            Personales de Chile.
          </Typography>

          <List dense disablePadding>
            <ListItem>
              <ListItemIcon>
                <FolderIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Escaneo de carpetas de red"
                secondary="Analiza archivos PDF, DOCX, XLSX, XLS, DOC, TXT, CSV y formatos de imagen (JPG, PNG) con OCR."
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <StorageIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Escaneo de bases de datos externas"
                secondary="Conecta con MySQL, PostgreSQL y SQL Server para analizar tablas y columnas específicas."
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <SearchIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Detección con IA (NLP) + patrones regex"
                secondary="Combina el motor NLP de Microsoft Presidio con reconocedores ad-hoc diseñados para PII chileno."
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <LockIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Datos sensibles cifrados con AES-256"
                secondary="Las categorías sensibles (salud, etnia, política, etc.) se almacenan cifradas con Fernet (AES-256)."
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <VisibilityOffIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Los datos nunca salen de tu red"
                secondary="El agente opera completamente on-premise. Solo se reportan métricas agregadas a la plataforma central UpShield."
              />
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* ================================================================ */}
      {/* SECTION 2 — Primeros Pasos                                      */}
      {/* ================================================================ */}
      <Accordion
        expanded={expanded === 'panel2'}
        onChange={handleChange('panel2')}
        elevation={0}
        sx={accordionSx}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={accordionSummarySx}>
          <Avatar sx={sectionIconSx('#28A745')}>
            <PlayArrowIcon fontSize="small" />
          </Avatar>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Primeros Pasos — Configuración Inicial
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stepper orientation="vertical" activeStep={-1}>
            {/* Step 1 */}
            <Step active>
              <StepLabel
                optional={<Typography variant="caption">Dashboard</Typography>}
              >
                <span style={{ fontWeight: 600 }}>Verificar Servicios</span>
              </StepLabel>
              <StepContent>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Ve al <strong>Dashboard</strong> y verifica que los indicadores de salud de los
                  servicios estén en verde:
                </Typography>
                <List dense disablePadding>
                  <ListItem disableGutters>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <CheckCircleIcon sx={{ color: '#28A745', fontSize: 18 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary="Apache Tika (extracción de texto)"
                      slotProps={{ primary: { variant: 'body2' as const } }}
                    />
                  </ListItem>
                  <ListItem disableGutters>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <CheckCircleIcon sx={{ color: '#28A745', fontSize: 18 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary="Microsoft Presidio (análisis PII)"
                      slotProps={{ primary: { variant: 'body2' as const } }}
                    />
                  </ListItem>
                </List>
                <Alert severity="warning" sx={{ mt: 1 }}>
                  Si algún indicador está en rojo, verifica que los contenedores Docker estén
                  corriendo con <code>docker compose ps</code>.
                </Alert>
              </StepContent>
            </Step>

            {/* Step 2 */}
            <Step active>
              <StepLabel optional={<Typography variant="caption">Configuración</Typography>}>
                <span style={{ fontWeight: 600 }}>Configurar Rutas de Red</span>
              </StepLabel>
              <StepContent>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Ve a <strong>Configuración</strong> y agrega las rutas de red que deseas escanear:
                </Typography>
                <List dense disablePadding>
                  <ListItem disableGutters>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <FolderIcon sx={{ fontSize: 18 }} color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <>
                          Rutas UNC: <code>\\\\servidor\\compartido</code>
                        </>
                      }
                      slotProps={{ primary: { variant: 'body2' as const } }}
                    />
                  </ListItem>
                  <ListItem disableGutters>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <FolderIcon sx={{ fontSize: 18 }} color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <>
                          Rutas locales: <code>C:\\datos\\documentos</code>
                        </>
                      }
                      slotProps={{ primary: { variant: 'body2' as const } }}
                    />
                  </ListItem>
                </List>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Selecciona las extensiones de archivo a escanear (PDF, DOCX, XLSX, TXT, CSV, JPG,
                  PNG, etc.).
                </Typography>
              </StepContent>
            </Step>

            {/* Step 3 */}
            <Step active>
              <StepLabel optional={<Typography variant="caption">Configuración</Typography>}>
                <span style={{ fontWeight: 600 }}>Configurar Bases de Datos</span>
              </StepLabel>
              <StepContent>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  En <strong>Configuración → Bases de Datos Externas</strong>, agrega las conexiones
                  a tus bases de datos:
                </Typography>
                <List dense disablePadding>
                  <ListItem disableGutters>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <StorageIcon sx={{ fontSize: 18 }} color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Ingresa el string de conexión (host, puerto, usuario, contraseña, base de datos)"
                      slotProps={{ primary: { variant: 'body2' as const } }}
                    />
                  </ListItem>
                  <ListItem disableGutters>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <StorageIcon sx={{ fontSize: 18 }} color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Selecciona las tablas y columnas específicas que deseas analizar"
                      slotProps={{ primary: { variant: 'body2' as const } }}
                    />
                  </ListItem>
                </List>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Motores soportados: <Chip label="MySQL" size="small" sx={{ mr: 0.5 }} />{' '}
                  <Chip label="PostgreSQL" size="small" sx={{ mr: 0.5 }} />{' '}
                  <Chip label="SQL Server" size="small" />
                </Typography>
              </StepContent>
            </Step>

            {/* Step 4 */}
            <Step active>
              <StepLabel optional={<Typography variant="caption">Entidades PII</Typography>}>
                <span style={{ fontWeight: 600 }}>Seleccionar Entidades a Detectar</span>
              </StepLabel>
              <StepContent>
                <Typography variant="body2" sx={{ mb: 1.5 }}>
                  Elige qué tipos de datos personales quieres detectar:
                </Typography>

                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Datos Básicos{' '}
                  <Chip
                    label="Básico"
                    size="small"
                    sx={{
                      ml: 1,
                      backgroundColor: 'rgba(108,117,125,0.1)',
                      color: '#6C757D',
                      fontWeight: 500,
                    }}
                  />
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                  {[
                    'RUT',
                    'Email',
                    'Persona',
                    'Teléfono',
                    'Fecha',
                    'Domicilio',
                    'Nacionalidad',
                    'Pasaporte',
                    'Licencia Conducir',
                    'Cuenta Bancaria',
                    'N° Serie Doc.',
                  ].map((e) => (
                    <Chip
                      key={e}
                      label={e}
                      size="small"
                      variant="outlined"
                      sx={{ borderColor: '#6C757D', color: '#6C757D' }}
                    />
                  ))}
                </Box>

                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Datos Sensibles{' '}
                  <Chip
                    label="Sensible — Cifrado"
                    size="small"
                    icon={<LockIcon sx={{ fontSize: 14 }} />}
                    sx={{
                      ml: 1,
                      backgroundColor: 'rgba(220,53,69,0.1)',
                      color: '#DC3545',
                      fontWeight: 500,
                      '& .MuiChip-icon': { color: '#DC3545' },
                    }}
                  />
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {[
                    'Salud',
                    'Etnia',
                    'Política',
                    'Religión',
                    'Sexualidad',
                    'Sindical',
                    'Socioeconómico',
                    'Ideología',
                    'Biológico',
                    'Biométrico',
                    'Penal',
                  ].map((e) => (
                    <Chip
                      key={e}
                      label={e}
                      size="small"
                      variant="outlined"
                      sx={{ borderColor: '#DC3545', color: '#DC3545' }}
                    />
                  ))}
                </Box>
              </StepContent>
            </Step>

            {/* Step 5 */}
            <Step active>
              <StepLabel optional={<Typography variant="caption">Dashboard</Typography>}>
                <span style={{ fontWeight: 600 }}>Lanzar Primer Escaneo</span>
              </StepLabel>
              <StepContent>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  En el <strong>Dashboard</strong>, haz clic en el botón{' '}
                  <Chip
                    label="Iniciar Escaneo"
                    size="small"
                    color="primary"
                    icon={<PlayArrowIcon sx={{ fontSize: 16 }} />}
                    sx={{ fontWeight: 500 }}
                  />
                  . La barra de progreso mostrará el avance en tiempo real.
                </Typography>
                <Alert severity="info" sx={{ mt: 1 }}>
                  El primer escaneo puede tardar más tiempo ya que debe procesar todos los archivos.
                  Los escaneos posteriores serán incrementales (solo archivos modificados).
                </Alert>
              </StepContent>
            </Step>
          </Stepper>
        </AccordionDetails>
      </Accordion>

      {/* ================================================================ */}
      {/* SECTION 3 — Entendiendo el Dashboard                            */}
      {/* ================================================================ */}
      <Accordion
        expanded={expanded === 'panel3'}
        onChange={handleChange('panel3')}
        elevation={0}
        sx={accordionSx}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={accordionSummarySx}>
          <Avatar sx={sectionIconSx('#17A2B8')}>
            <DashboardIcon fontSize="small" />
          </Avatar>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Entendiendo el Dashboard
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" sx={{ mb: 2 }}>
            El Dashboard presenta un resumen ejecutivo del estado de protección de datos de tu
            organización mediante tarjetas KPI y gráficos.
          </Typography>

          <List disablePadding>
            <ListItem sx={{ alignItems: 'flex-start' }}>
              <ListItemIcon>
                <Avatar sx={{ width: 32, height: 32, bgcolor: '#007BFF', fontSize: 14 }}>
                  <DescriptionIcon sx={{ fontSize: 18 }} />
                </Avatar>
              </ListItemIcon>
              <ListItemText
                primary={<span style={{ fontWeight: 600 }}>Archivos Escaneados</span>}
                secondary="Total de archivos procesados más celdas de base de datos analizadas. Incluye el conteo acumulado de todos los escaneos."
              />
            </ListItem>
            <Divider variant="inset" component="li" />

            <ListItem sx={{ alignItems: 'flex-start' }}>
              <ListItemIcon>
                <Avatar sx={{ width: 32, height: 32, bgcolor: '#FFC107', fontSize: 14 }}>
                  <SearchIcon sx={{ fontSize: 18 }} />
                </Avatar>
              </ListItemIcon>
              <ListItemText
                primary={<span style={{ fontWeight: 600 }}>Hallazgos PII</span>}
                secondary="Cantidad total de datos personales detectados en archivos y bases de datos."
              />
            </ListItem>
            <Divider variant="inset" component="li" />

            <ListItem sx={{ alignItems: 'flex-start' }}>
              <ListItemIcon>
                <Avatar sx={{ width: 32, height: 32, bgcolor: '#DC3545', fontSize: 14 }}>
                  <WarningIcon sx={{ fontSize: 18 }} />
                </Avatar>
              </ListItemIcon>
              <ListItemText
                primary={<span style={{ fontWeight: 600 }}>Nivel de Riesgo</span>}
                secondary="Calculado en base al porcentaje de hallazgos sensibles vs. básicos. A mayor proporción de datos sensibles, mayor riesgo."
              />
            </ListItem>
            <Divider variant="inset" component="li" />

            <ListItem sx={{ alignItems: 'flex-start' }}>
              <ListItemIcon>
                <Avatar sx={{ width: 32, height: 32, bgcolor: '#E74C3C', fontSize: 14 }}>
                  <LockIcon sx={{ fontSize: 18 }} />
                </Avatar>
              </ListItemIcon>
              <ListItemText
                primary={<span style={{ fontWeight: 600 }}>Datos Sensibles</span>}
                secondary="Conteo de hallazgos sensibles cifrados (salud, etnia, religión, política, etc.). Estos datos se almacenan cifrados con AES-256."
              />
            </ListItem>
          </List>

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle2" gutterBottom>
            Gráficos
          </Typography>
          <List dense disablePadding>
            <ListItem disableGutters>
              <ListItemIcon sx={{ minWidth: 32 }}>
                <CheckCircleIcon sx={{ fontSize: 16, color: '#28A745' }} />
              </ListItemIcon>
              <ListItemText
                primary="Distribución por tipo de entidad: gráfico de torta mostrando la proporción de cada categoría PII."
                slotProps={{ primary: { variant: 'body2' as const } }}
              />
            </ListItem>
            <ListItem disableGutters>
              <ListItemIcon sx={{ minWidth: 32 }}>
                <CheckCircleIcon sx={{ fontSize: 16, color: '#28A745' }} />
              </ListItemIcon>
              <ListItemText
                primary="Tendencia de riesgo: evolución temporal del nivel de riesgo en escaneos sucesivos."
                slotProps={{ primary: { variant: 'body2' as const } }}
              />
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* ================================================================ */}
      {/* SECTION 4 — Revisando Hallazgos                                 */}
      {/* ================================================================ */}
      <Accordion
        expanded={expanded === 'panel4'}
        onChange={handleChange('panel4')}
        elevation={0}
        sx={accordionSx}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={accordionSummarySx}>
          <Avatar sx={sectionIconSx('#E67E22')}>
            <SearchIcon fontSize="small" />
          </Avatar>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Revisando Hallazgos
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" sx={{ mb: 2 }}>
            La página de <strong>Hallazgos</strong> muestra todos los datos personales detectados
            durante los escaneos. Puedes explorar, filtrar y gestionar cada hallazgo.
          </Typography>

          <List disablePadding>
            <ListItem>
              <ListItemIcon>
                <SearchIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Filtros disponibles"
                secondary="Filtra por tipo de entidad, nivel de sensibilidad, o busca por RUT, email o nombre de persona."
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <DescriptionIcon color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Detalle del hallazgo"
                secondary="Haz clic en un hallazgo para ver: ruta del archivo, texto detectado, y puntuación de confianza (score)."
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <LockIcon sx={{ color: '#DC3545' }} />
              </ListItemIcon>
              <ListItemText
                primary="Datos sensibles cifrados"
                secondary='Los datos sensibles aparecen cifrados por defecto. Haz clic en "Descifrar" para verlos temporalmente.'
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleIcon sx={{ color: '#28A745' }} />
              </ListItemIcon>
              <ListItemText
                primary='Marcar como "Resuelto"'
                secondary="Una vez mitigado un hallazgo, márcalo como resuelto para actualizar las métricas del Dashboard."
              />
            </ListItem>
          </List>

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle2" gutterBottom>
            Niveles de Riesgo por Confianza
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              label="ALTO ≥ 0.85"
              size="small"
              sx={{ bgcolor: '#DC3545', color: '#FFFFFF', fontWeight: 600 }}
            />
            <Chip
              label="MEDIO 0.65 – 0.84"
              size="small"
              sx={{ bgcolor: '#FFC107', color: '#343A40', fontWeight: 600 }}
            />
            <Chip
              label="BAJO < 0.65"
              size="small"
              sx={{ bgcolor: '#28A745', color: '#FFFFFF', fontWeight: 600 }}
            />
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* ================================================================ */}
      {/* SECTION 5 — Mitigación — Censura de Archivos                    */}
      {/* ================================================================ */}
      <Accordion
        expanded={expanded === 'panel5'}
        onChange={handleChange('panel5')}
        elevation={0}
        sx={accordionSx}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={accordionSummarySx}>
          <Avatar sx={sectionIconSx('#8E44AD')}>
            <VisibilityOffIcon fontSize="small" />
          </Avatar>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Mitigación — Censura de Archivos
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" sx={{ mb: 2 }}>
            La plataforma ofrece <strong>tres modos de mitigación</strong> para proteger los datos personales
            detectados en archivos. Cada modo tiene un nivel distinto de intervención sobre el archivo original.
          </Typography>

          <Paper variant="outlined" sx={{ p: 2, mb: 2, borderRadius: 2, bgcolor: 'rgba(142,68,173,0.04)', borderColor: '#8E44AD' }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: '#8E44AD' }}>Modo 1: Generar y Descargar Copia Censurada (Página "Censura de Archivos")</Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Busca un titular por RUT, nombre o correo. Selecciona el archivo y haz clic en
              <strong> "Generar y Descargar Copia Censurada"</strong>. Se descarga una copia con los datos PII removidos.
            </Typography>
            <Alert severity="success" sx={{ mt: 1 }}>El archivo original <strong>NO se modifica</strong>. Se descarga una copia con sufijo <code>_censurado</code>.</Alert>
          </Paper>

          <Paper variant="outlined" sx={{ p: 2, mb: 2, borderRadius: 2, bgcolor: 'rgba(41,128,185,0.04)', borderColor: '#2980B9' }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: '#2980B9' }}>Modo 2: Censurar en Origen / Sobreescribir (Desde detalle del Hallazgo)</Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Desde la página <strong>Hallazgos</strong>, abre el detalle de un hallazgo y pulsa
              <strong> "Censurar en Origen (Sobreescribir)"</strong>. Esto aplica la censura directamente sobre el archivo original.
            </Typography>
            <Alert severity="warning" sx={{ mt: 1 }}><strong>¡Atención!</strong> Este modo <strong>SÍ modifica permanentemente</strong> el archivo original y marca todos los hallazgos del archivo como resueltos.</Alert>
          </Paper>

          <Paper variant="outlined" sx={{ p: 2, mb: 2, borderRadius: 2, bgcolor: 'rgba(255,193,7,0.06)', borderColor: '#FFC107' }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: '#E67E22' }}>Modo 3: Mover a Cuarentena (Desde detalle del Hallazgo)</Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Desde el detalle de un hallazgo, pulsa <strong>"Mover a Cuarentena"</strong>. El archivo se traslada
              a una carpeta segura y se deja un archivo <code>.quarantine.txt</code> en su lugar original.
            </Typography>
            <Alert severity="info" sx={{ mt: 1 }}>El archivo original es removido de su ubicación y protegido en cuarentena. Los hallazgos se marcan como resueltos.</Alert>
          </Paper>

          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" sx={{ mb: 1 }}>¿Qué ocurre según el tipo de archivo?</Typography>
          <List dense disablePadding>
            <ListItem><ListItemIcon><DescriptionIcon color="primary" /></ListItemIcon>
              <ListItemText primary="PDF" secondary="Se dibujan rectángulos negros sobre el texto PII detectado (censura visual permanente)." /></ListItem>
            <ListItem><ListItemIcon><DescriptionIcon color="primary" /></ListItemIcon>
              <ListItemText primary="TXT / CSV" secondary='El texto PII se reemplaza por la etiqueta [REDACTADO].' /></ListItem>
            <ListItem><ListItemIcon><DescriptionIcon color="primary" /></ListItemIcon>
              <ListItemText primary="Imágenes (JPG, PNG)" secondary="Se aplica OCR para localizar el texto y se dibujan cajas negras sobre las regiones donde se detectó PII." /></ListItem>
            <ListItem><ListItemIcon><DescriptionIcon sx={{ color: '#999' }} /></ListItemIcon>
              <ListItemText primary="DOCX / XLSX / XLS" secondary="Actualmente no soporta censura interna. Se genera una copia sin modificaciones." /></ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* ================================================================ */}
      {/* SECTION 6 — Derechos ARCO (DSAR)                                */}
      {/* ================================================================ */}
      <Accordion
        expanded={expanded === 'panel6'}
        onChange={handleChange('panel6')}
        elevation={0}
        sx={accordionSx}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={accordionSummarySx}>
          <Avatar sx={sectionIconSx('#2980B9')}>
            <GavelIcon fontSize="small" />
          </Avatar>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Derechos ARSOP (DSAR)
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" sx={{ mb: 2 }}>
            La Ley 21.719 otorga a los titulares de datos personales <strong>5 derechos fundamentales</strong>
            (ARSOP). La función DSAR permite responder a solicitudes de acceso de forma eficiente
            buscando todos los datos personales de un titular por su RUT.
          </Typography>

          <Paper variant="outlined" sx={{ p: 2, mb: 2, borderRadius: 2, bgcolor: 'rgba(41,128,185,0.04)', borderColor: '#2980B9' }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: '#2980B9' }}>¿Qué significa ARSOP?</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              <Chip label="A — Acceso" size="small" color="primary" variant="outlined" />
              <Chip label="R — Rectificación" size="small" color="primary" variant="outlined" />
              <Chip label="S — Supresión" size="small" color="primary" variant="outlined" />
              <Chip label="O — Oposición" size="small" color="primary" variant="outlined" />
              <Chip label="P — Portabilidad" size="small" color="primary" variant="outlined" />
            </Box>
          </Paper>

          <List disablePadding>
            <ListItem>
              <ListItemIcon><FingerprintIcon color="primary" /></ListItemIcon>
              <ListItemText
                primary="Buscar por RUT del titular"
                secondary='Ingresa el RUT del ciudadano chileno (con o sin puntos y guión). El sistema normaliza el formato automáticamente y busca en todos los archivos y bases de datos escaneados.'
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><DescriptionIcon color="primary" /></ListItemIcon>
              <ListItemText
                primary="Mapa de datos completo"
                secondary="El sistema muestra TODOS los archivos y tablas de BD donde se encontraron datos de esa persona, incluyendo el tipo de dato y si está cifrado."
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><LockIcon color="primary" /></ListItemIcon>
              <ListItemText
                primary="Descifrado al vuelo"
                secondary="Los datos sensibles se descifran temporalmente en pantalla para su revisión. Nunca se almacenan descifrados."
              />
            </ListItem>
          </List>

          <Alert severity="info" sx={{ mt: 2 }}>
            El resumen incluye un indicador de riesgo del titular: <strong>ALTO</strong> si tiene datos sensibles,
            <strong> MODERADO</strong> si solo tiene datos básicos, <strong>LIMPIO</strong> si no se encontraron datos.
          </Alert>
        </AccordionDetails>
      </Accordion>

      {/* ================================================================ */}
      {/* SECTION 7 — Gráfico de Identidad                                */}
      {/* ================================================================ */}
      <Accordion
        expanded={expanded === 'panel7'}
        onChange={handleChange('panel7')}
        elevation={0}
        sx={accordionSx}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={accordionSummarySx}>
          <Avatar sx={sectionIconSx('#1ABC9C')}>
            <HubIcon fontSize="small" />
          </Avatar>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Gráfico de Identidad
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" sx={{ mb: 2 }}>
            El <strong>Gráfico de Identidad</strong> correlaciona RUTs, nombres y correos encontrados
            en múltiples archivos y fuentes, mostrando una tabla con todos los titulares detectados.
          </Typography>

          <List disablePadding>
            <ListItem>
              <ListItemIcon><FingerprintIcon color="primary" /></ListItemIcon>
              <ListItemText
                primary="Tabla de titulares"
                secondary="Cada fila muestra: RUT, nombres asociados, correos, total de hallazgos, archivos relacionados y nivel de riesgo."
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><HubIcon color="primary" /></ListItemIcon>
              <ListItemText
                primary='Botón "Ver Grafo"'
                secondary="Al hacer clic se abre un panel lateral con un gráfico SVG radial que conecta al titular con todos los archivos donde se encontraron sus datos."
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><SearchIcon color="primary" /></ListItemIcon>
              <ListItemText
                primary="Búsqueda integrada"
                secondary="Filtra por RUT (con o sin formato), nombre o correo electrónico. Muestra cuántos titulares coinciden con la búsqueda."
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><WarningIcon sx={{ color: '#FFC107' }} /></ListItemIcon>
              <ListItemText
                primary="Detalle del titular"
                secondary="El panel lateral muestra nombres alternativos, correos, teléfonos y fechas de nacimiento asociadas, además de la lista de archivos involucrados."
              />
            </ListItem>
          </List>

          <Alert severity="info" sx={{ mt: 2 }}>
            Ideal para auditorías de cumplimiento: permite identificar qué personas tienen mayor
            exposición de datos y en cuántas fuentes distintas aparecen.
          </Alert>
        </AccordionDetails>
      </Accordion>

      {/* ================================================================ */}
      {/* SECTION 8 — Preguntas Frecuentes                                */}
      {/* ================================================================ */}
      <Accordion
        expanded={expanded === 'panel8'}
        onChange={handleChange('panel8')}
        elevation={0}
        sx={accordionSx}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={accordionSummarySx}>
          <Avatar sx={sectionIconSx('#FFC107')}>
            <TipsAndUpdatesIcon fontSize="small" />
          </Avatar>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Preguntas Frecuentes
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <List disablePadding>
            {(
              [
                {
                  q: '¿Qué pasa si el escaneo es muy lento?',
                  a: 'Puedes aumentar el parámetro max_workers en la configuración para procesar más archivos en paralelo. También activa el escaneo incremental para solo re-procesar archivos modificados.',
                },
                {
                  q: '¿Los datos sensibles se almacenan en texto plano?',
                  a: 'No. Todas las categorías sensibles (salud, etnia, política, religión, sexualidad, sindical, socioeconómico, ideología, biológico, biométrico, penal) se cifran con AES-256 (Fernet) antes de almacenarse en la base de datos.',
                },
                {
                  q: '¿Se modifica el archivo original al censurar?',
                  a: 'Depende del modo elegido. Desde la página "Censura de Archivos" se descarga una copia sin modificar el original. Pero desde el detalle de un hallazgo, la opción "Censurar en Origen" SÍ sobreescribe el archivo original permanentemente. También existe "Mover a Cuarentena" que retira el archivo de su ubicación.',
                },
                {
                  q: '¿Cada cuánto debo escanear?',
                  a: 'Se recomienda escanear carpetas de archivos semanalmente y bases de datos diariamente. Puedes configurar escaneos programados en la sección de Configuración.',
                },
                {
                  q: '¿Qué es el escaneo incremental?',
                  a: 'El escaneo incremental compara el hash MD5 de cada archivo con el hash almacenado del escaneo anterior. Solo se re-procesan archivos que han cambiado, reduciendo significativamente el tiempo de escaneo.',
                },
                {
                  q: '¿Cómo agrego una nueva base de datos?',
                  a: 'Ve a Configuración → sección Bases de Datos Externas → completa los datos de conexión (motor, host, puerto, usuario, contraseña, nombre de BD). Luego selecciona las tablas y columnas a escanear.',
                },
              ] as Array<{ q: string; a: string }>
            ).map((faq, idx) => (
              <React.Fragment key={idx}>
                <ListItem sx={{ flexDirection: 'column', alignItems: 'flex-start', py: 1.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, width: '100%' }}>
                    <TipsAndUpdatesIcon
                      sx={{ color: '#FFC107', mt: 0.3, fontSize: 20, flexShrink: 0 }}
                    />
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        {faq.q}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {faq.a}
                      </Typography>
                    </Box>
                  </Box>
                </ListItem>
                {idx < 5 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </AccordionDetails>
      </Accordion>

      {/* ================================================================ */}
      {/* SECTION 9 — Glosario de Términos                                */}
      {/* ================================================================ */}
      <Accordion
        expanded={expanded === 'panel9'}
        onChange={handleChange('panel9')}
        elevation={0}
        sx={accordionSx}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={accordionSummarySx}>
          <Avatar sx={sectionIconSx('#6C757D')}>
            <DescriptionIcon fontSize="small" />
          </Avatar>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Glosario de Términos
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <List disablePadding>
            {(
              [
                {
                  term: 'PII',
                  def: 'Personally Identifiable Information — Información de Identificación Personal. Cualquier dato que pueda identificar directa o indirectamente a una persona.',
                },
                {
                  term: 'DSAR',
                  def: 'Data Subject Access Request — Solicitud de Acceso del Titular (Solicitud ARCO en el marco legal chileno).',
                },
                {
                  term: 'Entidad Sensible',
                  def: 'Dato personal que requiere cifrado obligatorio según la Ley 21.719: salud, etnia, política, religión, sexualidad, sindical, socioeconómico, ideología, biológico, biométrico y penal.',
                },
                {
                  term: 'Escaneo Incremental',
                  def: 'Modo de escaneo que solo procesa archivos que han sido modificados desde el último escaneo, comparando hashes MD5.',
                },
                {
                  term: 'Presidio',
                  def: 'Motor de detección de PII desarrollado por Microsoft. Utiliza modelos NLP y reconocedores regex para identificar datos personales.',
                },
                {
                  term: 'Tika',
                  def: 'Motor de extracción de texto de Apache. Procesa archivos PDF, DOCX, XLSX e imágenes (OCR) para convertirlos a texto plano analizable.',
                },
                {
                  term: 'Fernet (AES-256)',
                  def: 'Estándar de cifrado simétrico utilizado para proteger datos sensibles. Garantiza que los datos cifrados no puedan leerse sin la clave maestra.',
                },
                {
                  term: 'RUT',
                  def: 'Rol Único Tributario — Número de identificación único asignado a personas naturales y jurídicas en Chile.',
                },
                {
                  term: 'ARSOP',
                  def: 'Derechos de Acceso, Rectificación, Supresión, Oposición y Portabilidad que la Ley 21.719 otorga a los titulares de datos personales.',
                },
              ] as Array<{ term: string; def: string }>
            ).map((item, idx, arr) => (
              <React.Fragment key={item.term}>
                <ListItem sx={{ py: 1.5, alignItems: 'flex-start' }}>
                  <ListItemIcon sx={{ minWidth: 40, mt: 0.5 }}>
                    <Chip
                      label={item.term}
                      size="small"
                      color="primary"
                      sx={{ fontWeight: 600, fontSize: '0.7rem' }}
                    />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="body2" color="text.secondary">
                        {item.def}
                      </Typography>
                    }
                  />
                </ListItem>
                {idx < arr.length - 1 && <Divider variant="inset" component="li" />}
              </React.Fragment>
            ))}
          </List>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default HelpCenter;
