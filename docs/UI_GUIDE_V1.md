# UpShield Edge Agent — UI/UX Design Guide V1

> **Version:** 1.0  
> **Last Updated:** 2026-06-04  
> **Status:** Living Document  
> **Based on:** UpShield Final — `theme.ts` & `ClientLayout.tsx`

---

## Table of Contents

1. [Overview & Design Philosophy](#1-overview--design-philosophy)
2. [Color Palette](#2-color-palette)
3. [Typography](#3-typography)
4. [Layout Structure](#4-layout-structure)
5. [Component Library](#5-component-library)
6. [PII-Specific Components](#6-pii-specific-components)
7. [Responsive Breakpoints](#7-responsive-breakpoints)
8. [Accessibility Standards](#8-accessibility-standards)
9. [Animation & Transitions](#9-animation--transitions)
10. [Do's and Don'ts](#10-dos-and-donts)

---

## 1. Overview & Design Philosophy

### Mission

The UpShield Edge Agent UI is a **professional-grade security dashboard** designed for data protection officers and compliance teams. Every design decision must reinforce **trust, clarity, and urgency** — the three pillars of a PII-protection interface.

### Core Principles

| Principle | Description |
|---|---|
| **Clarity First** | Data-dense screens must remain scannable. Use whitespace, hierarchy, and color coding to surface critical information instantly. |
| **Actionable Urgency** | Risk and scan results must convey severity at a glance through consistent color-coded risk levels (red/yellow/green). |
| **Professional Trust** | The interface must feel enterprise-grade. Avoid playful aesthetics; prefer clean lines, neutral backgrounds, and precise typography. |
| **Consistency** | All components share the same design tokens defined in this guide. Never introduce ad-hoc colors, spacings, or font sizes. |
| **Accessibility** | WCAG 2.1 AA compliance is mandatory. Minimum contrast ratios, keyboard navigation, and screen reader support are non-negotiable. |

### Technology Stack

- **Framework:** React 18+ with TypeScript
- **Component Library:** MUI (Material UI) v5+
- **Theming:** MUI `createTheme` with custom palette, typography, and component overrides
- **Icons:** `@mui/icons-material`
- **Charts:** Recharts or MUI X Charts
- **Data Grids:** MUI X DataGrid

---

## 2. Color Palette

### 2.1 Core Palette

| Token | Hex | Swatch | Usage |
|---|---|---|---|
| `primary.main` | `#007BFF` | 🟦 | Primary actions, active nav items, links, focus rings |
| `primary.contrastText` | `#FFFFFF` | ⬜ | Text on primary backgrounds |
| `primary.hover` | `#0056B3` | 🟦 | Button hover states, link hover |
| `secondary.main` | `#6C757D` | 🔘 | Secondary text, icons, inactive elements |
| `error.main` | `#DC3545` | 🟥 | Errors, destructive actions, HIGH risk level |
| `warning.main` | `#FFC107` | 🟨 | Warnings, MODERATE risk level |
| `success.main` | `#28A745` | 🟩 | Success states, CLEAN risk level, healthy services |
| `text.primary` | `#343A40` | ⬛ | Primary body text, headings |
| `text.secondary` | `#6C757D` | 🔘 | Secondary/supporting text, captions |
| `background.default` | `#F8F9FA` | ⬜ | Page background |
| `background.paper` | `#FFFFFF` | ⬜ | Cards, modals, paper surfaces |
| `divider` | `#E9ECEF` | ⬜ | Borders, dividers, input outlines |

### 2.2 Sidebar Palette

| Token | Hex | Usage |
|---|---|---|
| Sidebar Background | `#343A40` | Permanent sidebar background |
| Sidebar Text | `#CED4DA` | Default nav item text color |
| Sidebar Active | `#007BFF` | Active nav item background + icon tint |
| Content Background | `#F5F5F5` | Main content area background |

### 2.3 PII Entity Colors

| Entity Category | Hex | Usage |
|---|---|---|
| Salud (Health) | `#DC3545` | Health-related PII entities |
| Etnia (Ethnicity) | `#E67E22` | Ethnicity-related PII entities |
| Política (Politics) | `#8E44AD` | Political affiliation entities |
| Religión (Religion) | `#2980B9` | Religious affiliation entities |
| Sexualidad (Sexuality) | `#E91E63` | Sexual orientation or gender identity entities |
| Sindical (Labor Unions) | `#E67E22` | Labor union or professional association affiliation |
| Socioeconómico (Socioeconomics) | `#2ECC71` | Socioeconomic status, social registers, and subsidies |
| Ideología (Ideology) | `#9B59B6` | Ideological or philosophical convictions |
| Biológico (Biology) | `#1ABC9C` | Human biological profile, DNA, and blood types |
| Biométrico (Biometrics) | `#E74C3C` | Biometric data, fingerprints, and facial scans |
| Básico (Basic) | `#6C757D` | Standard PII (RUT, email, name) |

### 2.4 Usage in Code

```tsx
// theme.ts
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#007BFF',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#6C757D',
    },
    error: {
      main: '#DC3545',
    },
    warning: {
      main: '#FFC107',
    },
    success: {
      main: '#28A745',
    },
    text: {
      primary: '#343A40',
      secondary: '#6C757D',
    },
    background: {
      default: '#F8F9FA',
      paper: '#FFFFFF',
    },
    divider: '#E9ECEF',
  },
});
```

---

## 3. Typography

### 3.1 Font Family

**Inter** is the sole typeface across all UI surfaces. Load via Google Fonts:

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

### 3.2 Type Scale

| Variant | Size | Weight | Line Height | Usage |
|---|---|---|---|---|
| `h1` | `3rem` (48px) | 700 (Bold) | 1.2 | Page titles, hero headings |
| `h2` | `2.5rem` (40px) | 600 (SemiBold) | 1.3 | Section headings |
| `h3` | `2rem` (32px) | 600 (SemiBold) | 1.4 | Subsection headings, card titles |
| `h4` | `1.5rem` (24px) | 600 (SemiBold) | 1.4 | Widget headings |
| `h5` | `1.25rem` (20px) | 500 (Medium) | 1.5 | Minor headings |
| `h6` | `1rem` (16px) | 500 (Medium) | 1.5 | Overline headings |
| `body1` | `1rem` (16px) | 400 (Regular) | 1.6 | Primary body text |
| `body2` | `0.875rem` (14px) | 400 (Regular) | 1.6 | Secondary body text, table cells |
| `caption` | `0.75rem` (12px) | 400 (Regular) | 1.5 | Timestamps, footnotes |
| `button` | `0.875rem` (14px) | 500 (Medium) | 1.75 | Button labels |

### 3.3 Usage in Code

```tsx
// theme.ts — typography overrides
typography: {
  fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  h1: { fontSize: '3rem', fontWeight: 700 },
  h2: { fontSize: '2.5rem', fontWeight: 600 },
  h3: { fontSize: '2rem', fontWeight: 600 },
  body1: { fontSize: '1rem' },
  body2: { fontSize: '0.875rem' },
},
```

---

## 4. Layout Structure

### 4.1 Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Header (AppBar)                        │
│  [☰ Toggle]                          [Notifications] [👤]│
├────────┬─────────────────────────────────────────────────┤
│        │                                                 │
│  Side  │              Main Content                       │
│  bar   │              px:4 py:3                          │
│  280px │              bg: #F5F5F5                        │
│   or   │                                                 │
│  64px  │                                                 │
│        │                                                 │
│ #343A40│                                                 │
│        ├─────────────────────────────────────────────────┤
│        │              Footer (optional)                   │
└────────┴─────────────────────────────────────────────────┘
```

### 4.2 Header (AppBar)

| Property | Value |
|---|---|
| Position | `fixed` |
| Background | `#FFFFFF` |
| Box Shadow | `0 1px 3px rgba(0, 0, 0, 0.08)` |
| Border Bottom | `1px solid #E9ECEF` |
| Height | `64px` |
| Z-Index | `theme.zIndex.drawer + 1` |

```tsx
<AppBar
  position="fixed"
  sx={{
    backgroundColor: '#FFFFFF',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
    borderBottom: '1px solid #E9ECEF',
    zIndex: (theme) => theme.zIndex.drawer + 1,
  }}
>
  <Toolbar>
    {/* Toggle button — left */}
    <IconButton onClick={toggleSidebar}>
      <MenuIcon />
    </IconButton>

    <Box sx={{ flexGrow: 1 }} />

    {/* Notifications & Profile — right */}
    <IconButton><NotificationsIcon /></IconButton>
    <ProfileMenu />
  </Toolbar>
</AppBar>
```

### 4.3 Sidebar (Permanent Drawer)

| Property | Value |
|---|---|
| Variant | `permanent` |
| Width (Expanded) | `280px` |
| Width (Collapsed) | `64px` |
| Background | `#343A40` |
| Text Color | `#CED4DA` |
| Transition | `width 300ms ease` |

#### Sidebar Sections

1. **Logo Area** — Top of sidebar, separated by `border-bottom: 1px solid rgba(255,255,255,0.1)`
2. **Navigation Items** — Rounded `ListItemButton` with `borderRadius: 8px`
3. **Footer** — "Powered by UpShield" text at bottom

#### Active Navigation State

```tsx
<ListItemButton
  sx={{
    borderRadius: '8px',
    mx: 1,
    mb: 0.5,
    '&.Mui-selected': {
      backgroundColor: 'rgba(0, 123, 255, 0.15)',
      color: '#007BFF',
      '& .MuiListItemIcon-root': {
        color: '#007BFF',
      },
    },
    '&:hover': {
      backgroundColor: 'rgba(255, 255, 255, 0.08)',
    },
  }}
/>
```

### 4.4 Main Content Area

| Property | Value |
|---|---|
| Padding | `px: 4` (`32px`), `py: 3` (`24px`) |
| Background | `#F5F5F5` |
| Margin Left | Sidebar width (280px or 64px) |
| Margin Top | AppBar height (64px) |
| Transition | `margin-left 300ms ease` |

```tsx
<Box
  component="main"
  sx={{
    flexGrow: 1,
    px: 4,
    py: 3,
    mt: '64px',
    ml: sidebarOpen ? '280px' : '64px',
    backgroundColor: '#F5F5F5',
    minHeight: '100vh',
    transition: 'margin-left 300ms ease',
  }}
/>
```

---

## 5. Component Library

### 5.1 Buttons

#### Variants

| Variant | Usage | Example |
|---|---|---|
| `contained` | Primary actions (Save, Submit, Scan) | "Iniciar Escaneo" |
| `outlined` | Secondary actions (Cancel, Export) | "Cancelar" |
| `text` | Tertiary actions (View more, links) | "Ver Detalles" |

#### Styling Rules

- **Border Radius:** `4px`
- **Text Transform:** `none` (no uppercase)
- **Primary Hover:** `#0056B3`
- **Disabled Opacity:** `0.6`

```tsx
// theme.ts — component overrides
components: {
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 4,
        textTransform: 'none',
        fontWeight: 500,
        fontSize: '0.875rem',
      },
    },
  },
},
```

#### Examples

```tsx
{/* Primary Action */}
<Button variant="contained" color="primary" startIcon={<PlayArrowIcon />}>
  Iniciar Escaneo
</Button>

{/* Secondary Action */}
<Button variant="outlined" color="secondary">
  Cancelar
</Button>

{/* Destructive Action */}
<Button variant="contained" color="error" startIcon={<DeleteIcon />}>
  Eliminar
</Button>

{/* Success Action */}
<Button variant="contained" color="success">
  Aprobar
</Button>
```

### 5.2 Cards

Cards are the primary container for content grouping. Use `background.paper` (`#FFFFFF`) with subtle elevation.

| Property | Value |
|---|---|
| Background | `#FFFFFF` |
| Border Radius | `8px` |
| Border | `1px solid #E9ECEF` |
| Box Shadow | `0 1px 3px rgba(0, 0, 0, 0.06)` |
| Padding | `24px` |

```tsx
<Card
  sx={{
    borderRadius: '8px',
    border: '1px solid',
    borderColor: 'divider',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.06)',
  }}
>
  <CardContent sx={{ p: 3 }}>
    <Typography variant="h6" gutterBottom>
      Resumen de Escaneo
    </Typography>
    {/* Card content */}
  </CardContent>
</Card>
```

#### Card Variants

| Type | Extra Styling | Usage |
|---|---|---|
| **Stat Card** | Large number + caption below | KPI dashboard widgets |
| **Risk Card** | Left border `4px solid` in risk color | File/document risk summaries |
| **Status Card** | Colored icon badge top-right | Service health display |

```tsx
{/* Risk Card — left border indicates severity */}
<Card
  sx={{
    borderRadius: '8px',
    border: '1px solid #E9ECEF',
    borderLeft: '4px solid #DC3545', // ALTO risk
  }}
>
  <CardContent>
    <Typography variant="body2" color="text.secondary">
      Nivel de Riesgo
    </Typography>
    <Typography variant="h4" sx={{ color: '#DC3545', fontWeight: 700 }}>
      ALTO
    </Typography>
  </CardContent>
</Card>
```

### 5.3 Tables / DataGrid

Use MUI X DataGrid for all tabular data. Apply consistent theming:

| Property | Value |
|---|---|
| Header Background | `#F8F9FA` |
| Header Font Weight | `600` |
| Row Hover | `rgba(0, 123, 255, 0.04)` |
| Row Selected | `rgba(0, 123, 255, 0.08)` |
| Border Color | `#E9ECEF` |
| Cell Padding | `8px 16px` |
| Row Height | `52px` |

```tsx
<DataGrid
  rows={rows}
  columns={columns}
  pageSize={10}
  rowsPerPageOptions={[10, 25, 50]}
  disableSelectionOnClick
  sx={{
    border: '1px solid #E9ECEF',
    borderRadius: '8px',
    '& .MuiDataGrid-columnHeaders': {
      backgroundColor: '#F8F9FA',
      fontWeight: 600,
      fontSize: '0.875rem',
      borderBottom: '2px solid #E9ECEF',
    },
    '& .MuiDataGrid-row:hover': {
      backgroundColor: 'rgba(0, 123, 255, 0.04)',
    },
    '& .MuiDataGrid-cell': {
      borderBottom: '1px solid #E9ECEF',
      fontSize: '0.875rem',
    },
  }}
/>
```

### 5.4 Forms / TextFields

All text inputs use the `outlined` variant.

| Property | Value |
|---|---|
| Variant | `outlined` |
| Border Color (Default) | `#E9ECEF` |
| Border Color (Focus) | `#007BFF` |
| Border Radius | `4px` |
| Label Color | `#6C757D` |
| Label Color (Focused) | `#007BFF` |

```tsx
// theme.ts — TextField overrides
components: {
  MuiOutlinedInput: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-notchedOutline': {
          borderColor: '#E9ECEF',
        },
        '&:hover .MuiOutlinedInput-notchedOutline': {
          borderColor: '#007BFF',
        },
        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
          borderColor: '#007BFF',
        },
      },
    },
  },
},
```

#### Form Layout

```tsx
<Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
  <TextField
    label="Ruta del Directorio"
    variant="outlined"
    fullWidth
    placeholder="/ruta/a/escanear"
  />
  <TextField
    label="Expresión Regular"
    variant="outlined"
    fullWidth
    multiline
    rows={3}
  />
  <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
    <Button variant="outlined" color="secondary">Cancelar</Button>
    <Button variant="contained" color="primary">Guardar</Button>
  </Box>
</Box>
```

### 5.5 Badges / Chips

#### Risk Chips

```tsx
const riskChipStyles = {
  ALTO: { backgroundColor: '#DC3545', color: '#FFFFFF' },
  MODERADO: { backgroundColor: '#FFC107', color: '#343A40' },
  LIMPIO: { backgroundColor: '#28A745', color: '#FFFFFF' },
};

<Chip
  label="ALTO"
  size="small"
  sx={{
    ...riskChipStyles.ALTO,
    fontWeight: 600,
    fontSize: '0.75rem',
    borderRadius: '4px',
  }}
/>
```

#### Entity Category Chips

```tsx
const entityChipStyles = {
  Salud:      { backgroundColor: 'rgba(220, 53, 69, 0.1)',  color: '#DC3545' },
  Etnia:      { backgroundColor: 'rgba(230, 126, 34, 0.1)', color: '#E67E22' },
  Política:   { backgroundColor: 'rgba(142, 68, 173, 0.1)', color: '#8E44AD' },
  Religión:   { backgroundColor: 'rgba(41, 128, 185, 0.1)', color: '#2980B9' },
  Sexualidad: { backgroundColor: 'rgba(233, 30, 99, 0.1)',  color: '#E91E63' },
  Básico:     { backgroundColor: 'rgba(108, 117, 125, 0.1)', color: '#6C757D' },
};

<Chip
  icon={<LocalHospitalIcon />}
  label="Salud"
  size="small"
  sx={{
    ...entityChipStyles.Salud,
    fontWeight: 500,
    borderRadius: '16px',
  }}
/>
```

#### Status Badges

| Status | Color | Label |
|---|---|---|
| Active / Online | `#28A745` | Activo |
| Warning / Degraded | `#FFC107` | Degradado |
| Error / Offline | `#DC3545` | Sin Conexión |
| Idle / Unknown | `#6C757D` | Inactivo |

### 5.6 Charts

Use Recharts or MUI X Charts. Apply the UpShield palette consistently:

| Chart Type | Usage | Color Strategy |
|---|---|---|
| **Donut/Pie** | Entity type distribution | Entity category colors |
| **Bar** | Files per risk level | Risk level colors |
| **Line/Area** | Scan history over time | Primary (`#007BFF`) |
| **Stacked Bar** | Multi-category breakdown | Ordered palette sequence |

#### Chart Color Sequence (for multi-series)

```ts
const chartPalette = [
  '#007BFF', // Primary
  '#28A745', // Success
  '#FFC107', // Warning
  '#DC3545', // Error
  '#6C757D', // Secondary
  '#E67E22', // Etnia
  '#8E44AD', // Política
  '#2980B9', // Religión
  '#E91E63', // Sexualidad
];
```

#### Example — Risk Distribution Donut

```tsx
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Alto', value: 12, color: '#DC3545' },
  { name: 'Moderado', value: 28, color: '#FFC107' },
  { name: 'Limpio', value: 60, color: '#28A745' },
];

<ResponsiveContainer width="100%" height={250}>
  <PieChart>
    <Pie
      data={data}
      innerRadius={60}
      outerRadius={90}
      dataKey="value"
      paddingAngle={2}
    >
      {data.map((entry, i) => (
        <Cell key={i} fill={entry.color} />
      ))}
    </Pie>
    <Tooltip />
  </PieChart>
</ResponsiveContainer>
```

---

## 6. PII-Specific Components

### 6.1 Risk Level Badges

Risk levels map directly to the severity of PII findings in a file or directory.

| Level | Hex | Background (Light) | Label | Meaning |
|---|---|---|---|---|
| **ALTO** | `#DC3545` | `rgba(220,53,69,0.1)` | Alto | Sensitive PII (health, ethnicity, politics, religion, sexuality) |
| **MODERADO** | `#FFC107` | `rgba(255,193,7,0.1)` | Moderado | Standard PII (RUT, email, phone, name) |
| **LIMPIO** | `#28A745` | `rgba(40,167,69,0.1)` | Limpio | No PII detected |

```tsx
interface RiskBadgeProps {
  level: 'ALTO' | 'MODERADO' | 'LIMPIO';
}

const RiskBadge: React.FC<RiskBadgeProps> = ({ level }) => {
  const config = {
    ALTO:     { bg: '#DC3545', text: '#FFFFFF', icon: <WarningIcon /> },
    MODERADO: { bg: '#FFC107', text: '#343A40', icon: <InfoIcon /> },
    LIMPIO:   { bg: '#28A745', text: '#FFFFFF', icon: <CheckCircleIcon /> },
  };

  const { bg, text, icon } = config[level];

  return (
    <Chip
      icon={icon}
      label={level}
      sx={{
        backgroundColor: bg,
        color: text,
        fontWeight: 700,
        fontSize: '0.75rem',
        borderRadius: '4px',
        '& .MuiChip-icon': { color: text },
      }}
    />
  );
};
```

### 6.2 Entity Type Icons

Each PII entity type has a dedicated icon to enable rapid visual identification.

| Entity Type | Icon | Import | Color |
|---|---|---|---|
| RUT (ID Number) | `BadgeIcon` | `@mui/icons-material/Badge` | `#6C757D` |
| Email | `EmailIcon` | `@mui/icons-material/Email` | `#6C757D` |
| Nombre (Name) | `PersonIcon` | `@mui/icons-material/Person` | `#6C757D` |
| Salud (Health) | `LocalHospitalIcon` | `@mui/icons-material/LocalHospital` | `#DC3545` |
| Etnia (Ethnicity) | `GroupsIcon` | `@mui/icons-material/Groups` | `#E67E22` |
| Política (Politics) | `GavelIcon` | `@mui/icons-material/Gavel` | `#8E44AD` |
| Religión (Religion) | `AccountBalanceIcon` | `@mui/icons-material/AccountBalance` | `#2980B9` |
| Sexualidad (Sexuality) | `FavoriteIcon` | `@mui/icons-material/Favorite` | `#E91E63` |
| Sindical (Labor Unions) | `Diversity3Icon` | `@mui/icons-material/Diversity3` | `#E67E22` |
| Socioeconómico (Socioeconomics) | `AccountBalanceWalletIcon` | `@mui/icons-material/AccountBalanceWallet` | `#2ECC71` |
| Ideología (Ideology) | `PsychologyIcon` | `@mui/icons-material/Psychology` | `#9B59B6` |
| Biológico (Biology) | `BiotechIcon` | `@mui/icons-material/Biotech` | `#1ABC9C` |
| Biométrico (Biometrics) | `FingerprintIcon` | `@mui/icons-material/Fingerprint` | `#E74C3C` |

```tsx
import BadgeIcon from '@mui/icons-material/Badge';
import EmailIcon from '@mui/icons-material/Email';
import PersonIcon from '@mui/icons-material/Person';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import GroupsIcon from '@mui/icons-material/Groups';
import GavelIcon from '@mui/icons-material/Gavel';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import BiotechIcon from '@mui/icons-material/Biotech';
import PsychologyIcon from '@mui/icons-material/Psychology';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import Diversity3Icon from '@mui/icons-material/Diversity3';

const ENTITY_ICON_MAP: Record<string, { icon: React.ReactElement; color: string }> = {
  rut:            { icon: <BadgeIcon />,                  color: '#6C757D' },
  email:          { icon: <EmailIcon />,                  color: '#6C757D' },
  nombre:         { icon: <PersonIcon />,                 color: '#6C757D' },
  salud:          { icon: <LocalHospitalIcon />,          color: '#DC3545' },
  etnia:          { icon: <GroupsIcon />,                 color: '#E67E22' },
  politica:       { icon: <GavelIcon />,                  color: '#8E44AD' },
  religion:       { icon: <AccountBalanceIcon />,         color: '#2980B9' },
  sexualidad:     { icon: <FavoriteIcon />,               color: '#E91E63' },
  sindical:       { icon: <Diversity3Icon />,             color: '#E67E22' },
  socioeconomico: { icon: <AccountBalanceWalletIcon />,   color: '#2ECC71' },
  ideologia:      { icon: <PsychologyIcon />,             color: '#9B59B6' },
  biologico:      { icon: <BiotechIcon />,                color: '#1ABC9C' },
  biometrico:     { icon: <FingerprintIcon />,            color: '#E74C3C' },
};
```

### 6.3 Scan Status Indicator

The scan status component represents the lifecycle of a PII scan.

| State | Visual | Description |
|---|---|---|
| **Idle** | Grey circle + "Listo" | No scan in progress |
| **Running** | Animated progress ring + percentage | Scan actively processing files |
| **Completed** | Green checkmark + summary stats | Scan finished successfully |
| **Error** | Red X + error message | Scan encountered a fatal error |

```tsx
interface ScanStatusProps {
  status: 'idle' | 'running' | 'completed' | 'error';
  progress?: number;   // 0–100, only for 'running'
  message?: string;
}

const ScanStatus: React.FC<ScanStatusProps> = ({ status, progress, message }) => {
  switch (status) {
    case 'idle':
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CircleIcon sx={{ color: '#6C757D', fontSize: 12 }} />
          <Typography variant="body2" color="text.secondary">Listo para escanear</Typography>
        </Box>
      );

    case 'running':
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <CircularProgress
            variant="determinate"
            value={progress}
            size={40}
            thickness={4}
            sx={{
              color: '#007BFF',
              animation: 'pulse 2s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': { opacity: 1 },
                '50%': { opacity: 0.7 },
              },
            }}
          />
          <Box>
            <Typography variant="body2" fontWeight={600}>
              Escaneando... {progress}%
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {message}
            </Typography>
          </Box>
        </Box>
      );

    case 'completed':
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CheckCircleIcon sx={{ color: '#28A745' }} />
          <Typography variant="body2" sx={{ color: '#28A745', fontWeight: 600 }}>
            Escaneo completado
          </Typography>
        </Box>
      );

    case 'error':
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ErrorIcon sx={{ color: '#DC3545' }} />
          <Typography variant="body2" sx={{ color: '#DC3545', fontWeight: 600 }}>
            Error: {message}
          </Typography>
        </Box>
      );
  }
};
```

### 6.4 Service Health Indicators

Traffic-light style indicators show the health of backend microservices.

| State | Color | Size | Label |
|---|---|---|---|
| **Healthy** | `#28A745` | 12px circle | Conectado |
| **Unhealthy** | `#DC3545` | 12px circle | Sin Conexión |
| **Degraded** | `#FFC107` | 12px circle | Degradado |

```tsx
interface ServiceHealthProps {
  name: string;
  status: 'healthy' | 'unhealthy' | 'degraded';
  latency?: number; // ms
}

const ServiceHealth: React.FC<ServiceHealthProps> = ({ name, status, latency }) => {
  const colorMap = {
    healthy: '#28A745',
    unhealthy: '#DC3545',
    degraded: '#FFC107',
  };

  const labelMap = {
    healthy: 'Conectado',
    unhealthy: 'Sin Conexión',
    degraded: 'Degradado',
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
      <Box
        sx={{
          width: 12,
          height: 12,
          borderRadius: '50%',
          backgroundColor: colorMap[status],
          boxShadow: `0 0 6px ${colorMap[status]}40`,
        }}
      />
      <Box>
        <Typography variant="body2" fontWeight={500}>{name}</Typography>
        <Typography variant="caption" color="text.secondary">
          {labelMap[status]}
          {latency !== undefined && ` · ${latency}ms`}
        </Typography>
      </Box>
    </Box>
  );
};
```

---

## 7. Responsive Breakpoints

Use MUI's default breakpoint system. All layouts must be functional from `sm` upward; `xs` is a best-effort mobile view.

| Breakpoint | Min Width | Sidebar Behavior | Grid Columns |
|---|---|---|---|
| `xs` | 0px | Hidden (overlay drawer) | 1 |
| `sm` | 600px | Collapsed (64px) | 1–2 |
| `md` | 900px | Collapsed (64px) | 2–3 |
| `lg` | 1200px | Expanded (280px) | 3–4 |
| `xl` | 1536px | Expanded (280px) | 4+ |

### Responsive Patterns

```tsx
{/* Responsive grid layout */}
<Grid container spacing={3}>
  <Grid item xs={12} md={6} lg={3}>
    <StatCard title="Archivos Escaneados" value={1284} />
  </Grid>
  <Grid item xs={12} md={6} lg={3}>
    <StatCard title="Riesgo Alto" value={12} color="error" />
  </Grid>
  <Grid item xs={12} md={6} lg={3}>
    <StatCard title="Riesgo Moderado" value={28} color="warning" />
  </Grid>
  <Grid item xs={12} md={6} lg={3}>
    <StatCard title="Limpios" value={1244} color="success" />
  </Grid>
</Grid>
```

### Sidebar Responsive Logic

```tsx
const isMobile = useMediaQuery(theme.breakpoints.down('md'));
const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));

// Mobile: temporary drawer (overlay)
// Tablet: permanent drawer, collapsed (64px)
// Desktop: permanent drawer, expanded (280px) or collapsed by toggle
```

---

## 8. Accessibility Standards

### 8.1 Requirements

| Standard | Target |
|---|---|
| WCAG Level | **2.1 AA** |
| Contrast Ratio (normal text) | ≥ **4.5:1** |
| Contrast Ratio (large text) | ≥ **3:1** |
| Focus Indicator | Visible `2px solid #007BFF` outline |
| Keyboard Navigation | Full support for all interactive elements |
| Screen Reader | Semantic HTML + ARIA labels |

### 8.2 Color Contrast Verification

| Combination | Ratio | Pass? |
|---|---|---|
| `#343A40` on `#FFFFFF` | 10.7:1 | ✅ AAA |
| `#6C757D` on `#FFFFFF` | 4.6:1 | ✅ AA |
| `#FFFFFF` on `#007BFF` | 4.6:1 | ✅ AA |
| `#FFFFFF` on `#DC3545` | 4.5:1 | ✅ AA |
| `#343A40` on `#FFC107` | 8.2:1 | ✅ AAA |
| `#FFFFFF` on `#28A745` | 3.5:1 | ⚠️ Large text only |
| `#CED4DA` on `#343A40` | 7.8:1 | ✅ AAA |

> [!WARNING]
> `#FFFFFF` on `#28A745` (success green) fails AA for normal text. Use `#FFFFFF` only for large/bold text on success green backgrounds, or darken the green to `#1E7E34` for small text contexts.

### 8.3 Keyboard Navigation

```tsx
{/* All interactive elements must be focusable and keyboard-operable */}
<Button
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleAction();
    }
  }}
>
  Acción
</Button>

{/* Focus ring styling */}
'&:focus-visible': {
  outline: '2px solid #007BFF',
  outlineOffset: '2px',
}
```

### 8.4 ARIA Labels

```tsx
{/* Always provide aria-labels for icon-only buttons */}
<IconButton aria-label="Abrir menú de perfil">
  <AccountCircleIcon />
</IconButton>

{/* Announce dynamic status changes */}
<Box role="status" aria-live="polite">
  <Typography>Escaneo completado: 42 archivos procesados</Typography>
</Box>

{/* Label complex components */}
<DataGrid
  aria-label="Tabla de resultados de escaneo PII"
  columns={columns}
  rows={rows}
/>
```

---

## 9. Animation & Transitions

### 9.1 Core Timing

| Token | Duration | Easing | Usage |
|---|---|---|---|
| `--transition-fast` | `150ms` | `ease` | Hover states, color changes |
| `--transition-normal` | `300ms` | `ease` | Sidebar open/close, page transitions |
| `--transition-slow` | `500ms` | `ease-in-out` | Modal entrance, chart renders |

### 9.2 Sidebar Transition

```tsx
// Sidebar width transition
transition: 'width 300ms ease',

// Content area margin transition
transition: 'margin-left 300ms ease',
```

### 9.3 Component Animations

#### Loading Skeleton

```tsx
<Skeleton
  variant="rectangular"
  height={200}
  sx={{
    borderRadius: '8px',
    animation: 'wave 1.5s ease-in-out infinite',
  }}
/>
```

#### Scan Progress Pulse

```tsx
const pulseAnimation = {
  '@keyframes pulse': {
    '0%, 100%': { opacity: 1, transform: 'scale(1)' },
    '50%': { opacity: 0.7, transform: 'scale(1.05)' },
  },
  animation: 'pulse 2s ease-in-out infinite',
};
```

#### Fade-in on Mount

```tsx
import { Fade } from '@mui/material';

<Fade in timeout={500}>
  <Card>
    {/* Content fades in on page load */}
  </Card>
</Fade>
```

#### Row Highlight on New Data

```tsx
const highlightRow = {
  '@keyframes highlightFade': {
    '0%': { backgroundColor: 'rgba(0, 123, 255, 0.15)' },
    '100%': { backgroundColor: 'transparent' },
  },
  animation: 'highlightFade 2s ease-out',
};
```

### 9.4 Performance Rules

> [!IMPORTANT]
> - Only animate `transform` and `opacity` for GPU-accelerated performance.
> - Use `will-change: transform` sparingly and only on elements that will animate.
> - Prefer CSS transitions over JavaScript-driven animations.
> - Disable animations when `prefers-reduced-motion: reduce` is active.

```tsx
'@media (prefers-reduced-motion: reduce)': {
  animation: 'none !important',
  transition: 'none !important',
},
```

---

## 10. Do's and Don'ts

### ✅ Do

| # | Guideline |
|---|---|
| 1 | **Use design tokens** from this guide for all colors, spacings, and font sizes. |
| 2 | **Apply risk colors consistently:** `#DC3545` = ALTO, `#FFC107` = MODERADO, `#28A745` = LIMPIO. |
| 3 | **Use Inter font** for all text. Never mix typefaces. |
| 4 | **Include aria-labels** on all icon-only buttons and interactive elements. |
| 5 | **Use the 8px grid** for spacing (multiples of 8: 8, 16, 24, 32, 40, 48). |
| 6 | **Keep cards clean** with consistent padding (`24px`) and border radius (`8px`). |
| 7 | **Show loading states** (Skeleton or CircularProgress) while data is fetching. |
| 8 | **Use `outlined` variant** for all TextFields. |
| 9 | **Set `textTransform: 'none'`** on all buttons — avoid ALL CAPS labels. |
| 10 | **Provide visual feedback** for every user interaction (hover, focus, active states). |
| 11 | **Test with keyboard only** — every workflow must be completable without a mouse. |
| 12 | **Use MUI's `sx` prop** or theme overrides for styling. Avoid inline `style` props. |

### ❌ Don't

| # | Anti-Pattern | Why |
|---|---|---|
| 1 | **Don't use ad-hoc colors.** | Every color must exist in the palette defined above. Random hex values break consistency. |
| 2 | **Don't use `text-transform: uppercase`** on buttons. | Our design uses sentence case. |
| 3 | **Don't hardcode pixel widths** for responsive layouts. | Use MUI Grid and breakpoints. |
| 4 | **Don't skip empty states.** | Always show an illustration or message when a table/list has no data. |
| 5 | **Don't use browser-default fonts.** | Always ensure Inter is loaded; use the system font stack as fallback only. |
| 6 | **Don't animate layout properties** (`width`, `height`, `margin`). | Animate `transform` and `opacity` for performance. Sidebar is the one exception. |
| 7 | **Don't use raw color hex in components.** | Reference `theme.palette.*` or `sx={{ color: 'error.main' }}`. |
| 8 | **Don't remove focus outlines.** | Users who navigate by keyboard rely on visible focus rings. |
| 9 | **Don't mix Chip shapes.** | Use `borderRadius: 4px` for status chips, `borderRadius: 16px` for entity category chips. |
| 10 | **Don't use alerts/snackbars without auto-dismiss.** | Success messages should auto-dismiss after 4s. Errors persist until dismissed by user. |

---

## Appendix: Quick Reference Cheat Sheet

### Spacing Scale (8px grid)

| Token | Value |
|---|---|
| `0.5` | 4px |
| `1` | 8px |
| `1.5` | 12px |
| `2` | 16px |
| `3` | 24px |
| `4` | 32px |
| `5` | 40px |
| `6` | 48px |

### Z-Index Layers

| Layer | Z-Index | Usage |
|---|---|---|
| Content | `0` | Page content |
| Sticky Headers | `100` | Table headers, sub-navs |
| Sidebar | `1200` | Navigation drawer |
| AppBar | `1201` | Top navigation bar |
| Modal Backdrop | `1300` | Modal overlay |
| Modal | `1400` | Modal content |
| Snackbar | `1500` | Toast notifications |
| Tooltip | `1600` | Tooltips |

### Icon Sizing

| Context | Size |
|---|---|
| Navigation items | `24px` (default) |
| Inline with text | `20px` (`fontSize="small"`) |
| Feature highlights | `40px` (`fontSize="large"`) |
| Empty states | `64px` |

---

> **This is a living document.** Update this guide whenever new components, patterns, or design decisions are introduced. All changes must be reviewed to ensure consistency with the established design system.
