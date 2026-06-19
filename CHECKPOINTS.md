# CHECKPOINTS.md — Criterios objetivos de "estado final correcto"

> Este archivo define qué significa **"hecho bien"** en el Edge Agent de UpShield.
> No se puede declarar una tarea como `done` sin que TODOS los checkpoints aplicables estén verdes.
> **Criterios objetivos, no opiniones.**

---

## Checkpoints globales

### CHK-GLOB-001 — Tests backend verdes
**Cómo verificar:** `cd edge_backend && pytest` → 0 errores nuevos.

### CHK-GLOB-002 — TypeCheck frontend verde
**Cómo verificar:** `cd edge_frontend && npm run type-check` → 0 errores nuevos.

### CHK-GLOB-003 — Lint frontend verde
**Cómo verificar:** `cd edge_frontend && npm run lint` → 0 errores nuevos.

### CHK-GLOB-004 — No hay `console.log` ni `TODO` sin issue
**Cómo verificar:** `grep -rn "console\.log\|FIXME\|XXX"` en archivos modificados. Solo permitido en tests.

### CHK-GLOB-005 — `progress/current.md` actualizado
**Cómo verificar:** el archivo refleja el estado actual de la sesión.

### CHK-GLOB-006 — Entrada nueva en `progress/history.md`
**Cómo verificar:** hay una entrada nueva al cierre de la sesión.

---

## Checkpoints de PII Discovery

### CHK-PII-001 — Datos sensibles cifrados en BD
**Cómo verificar:** queries directas a MySQL muestran texto cifrado (Fernet) para entidades DATA_SALUD, DATA_ETNIA, DATA_POLITICA, DATA_RELIGION, DATA_SEXUALIDAD. Nunca texto plano.

### CHK-PII-002 — Descifrado solo al vuelo en API
**Cómo verificar:** grep en routers/services — `cipher_suite.decrypt()` solo se llama dentro de endpoints que lo requieren explícitamente (DSAR, finding detail). Nunca en listados masivos ni exports.

### CHK-PII-003 — Health check antes de escaneo
**Cómo verificar:** `scan_engine.start_scan()` verifica que Tika y Presidio responden antes de procesar archivos. Si alguno falla, el escaneo se aborta con error descriptivo.

---

## Checkpoints de migraciones

### CHK-MIG-001 — Migración Alembic aplicada sin errores
**Cómo verificar:** `cd edge_backend && alembic upgrade head` completa sin errores.

### CHK-MIG-002 — Rollback funciona
**Cómo verificar:** `alembic downgrade -1` completa sin errores (solo en dev).

---

## Checkpoints de UI

### CHK-UI-001 — Sigue guía de diseño
**Cómo verificar:** los componentes usan tema MUI de theme.ts y siguen docs/UI_GUIDE_V1.md.

### CHK-UI-002 — Responsive
**Cómo verificar:** la UI no se rompe en breakpoints estándar MUI (xs, sm, md, lg, xl).

### CHK-UI-003 — Accesibilidad básica
**Cómo verificar:** inputs tienen label, botones tienen aria-label, contraste suficiente.

---

## Checkpoints de servicios Docker

### CHK-SVC-001 — Docker Compose levanta los 4 servicios
**Cómo verificar:** `docker compose up -d && docker compose ps` muestra tika, presidio, edge-backend, edge-frontend todos en estado running.

### CHK-SVC-002 — Nginx proxy funciona
**Cómo verificar:** `curl http://localhost:3000/api/health` retorna JSON del backend (no error de Nginx).

---

## Cuándo añadir nuevos checkpoints

Cada vez que se descubra un bug por una razón no cubierta por un checkpoint existente, añádelo aquí.
