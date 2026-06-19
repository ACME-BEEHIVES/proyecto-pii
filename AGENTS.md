# AGENTS.md — Mapa del repositorio para agentes de IA

> Este archivo es el **punto de entrada** para cualquier agente que trabaje en este repositorio.
> NO es una biblia de reglas: es un **mapa**. Lee solo lo que necesites cuando lo necesites.
> Si encuentras información obsoleta, **párate y avisa**. No improvises.

---

## 1. Antes de empezar (obligatorio en cada sesión)

1. **Ejecuta `.\init.ps1`** y verifica que termina sin errores rojos.
2. Lee `progress/current.md` para entender en qué estado quedó la última sesión.
3. Lee `feature_list.json` y elige **UNA** tarea con estado `pending`, o continúa la que esté `in_progress`. **Nunca trabajes en más de una a la vez.**
4. Si la tarea es compleja (toca >3 archivos, varias capas), **crea un `implementation_plan.md`** y espera aprobación.
5. Antes de declarar `done`, verifica contra `CHECKPOINTS.md`.

---

## 2. Qué es este proyecto

**UpShield Edge Agent** es el componente on-premise de la plataforma UpShield. Opera dentro de la red del cliente para escanear archivos e imágenes en busca de datos personales sensibles bajo la **Ley 21.719 (Chile)**. Es una aplicación independiente con su propio frontend y backend que se comunica con la plataforma central UpShield vía API REST.

### Stack

| Capa | Tecnología |
|---|---|
| **Backend** | Python 3.12 · FastAPI · SQLAlchemy · Alembic |
| **Frontend** | React 19 · TypeScript · Vite · MUI 6 |
| **Base de datos** | MySQL 8.0 (local, esquema `pii_discovery`) |
| **Extracción texto** | Apache Tika (Docker, puerto 9998) |
| **Análisis NLP** | Microsoft Presidio (Docker, puerto 5001) |
| **Criptografía** | AES-256 (Fernet) |
| **Comunicación** | REST API hacia UpShield central |

### Estructura del proyecto

```
proyecto-pii/
├── AGENTS.md, CHECKPOINTS.md, feature_list.json, init.ps1
├── progress/                    ← Estado de sesión
├── docs/UI_GUIDE_V1.md          ← Guía de diseño UI/UX
├── docker-compose.yml           ← Tika + Presidio + Backend + Frontend
├── edge_backend/                ← API FastAPI
│   ├── app/main.py              ← Punto de entrada
│   ├── app/database.py          ← SQLAlchemy engine
│   ├── app/config.py            ← Pydantic BaseSettings
│   ├── app/models/              ← Modelos SQLAlchemy
│   ├── app/routers/             ← Endpoints FastAPI
│   ├── app/services/            ← Lógica de negocio
│   ├── app/schemas/             ← Pydantic schemas
│   └── alembic/                 ← Migraciones BD
├── edge_frontend/               ← Webapp React
│   ├── src/App.tsx              ← Router principal
│   ├── src/theme.ts             ← Tema MUI
│   ├── src/components/          ← Componentes React
│   ├── src/pages/               ← Vistas
│   └── src/services/api.ts      ← Cliente API
├── analyzer.yaml                ← Config Presidio
├── registry.yaml                ← Config Presidio
└── motor_pii_v4_incremental.py  ← Motor original (referencia)
```

---

## 3. Mapa del repositorio

| Archivo / carpeta | Qué contiene | Cuándo leerlo |
|---|---|---|
| `feature_list.json` | Tablero de tareas | **Siempre, al empezar** |
| `progress/current.md` | Estado de sesión actual | **Siempre, al empezar** |
| `progress/history.md` | Bitácora de sesiones | Si necesitas contexto histórico |
| `AGENTS.md` (este archivo) | Mapa de navegación | Por defecto al empezar |
| `CHECKPOINTS.md` | Criterios de verificación | Antes de declarar done |
| `docs/UI_GUIDE_V1.md` | Guía de diseño UI/UX | Cuando toques frontend |
| `edge_backend/app/main.py` | Registra routers | Cuando añadas endpoints |
| `edge_backend/app/database.py` | Engine SQLAlchemy | Cuando toques BD |
| `edge_backend/app/config.py` | Settings del .env | Cuando añadas config |
| `edge_backend/app/services/scan_engine.py` | Motor de escaneo PII | Cuando toques escaneo |
| `edge_backend/app/services/crypto_service.py` | Cifrado/descifrado | Cuando toques datos sensibles |
| `edge_frontend/src/theme.ts` | Tema MUI | Cuando toques estilos |
| `edge_frontend/src/App.tsx` | Router React | Cuando añadas páginas |
| `motor_pii_v4_incremental.py` | Motor original | Como referencia de lógica |
| `docker-compose.yml` | Servicios Docker | Cuando toques infraestructura |

---

## 4. Comandos canónicos

```powershell
# ========== BACKEND (desde edge_backend/) ==========
uvicorn app.main:app --reload --port 8001     # Dev con hot-reload
pytest                                         # Tests
pytest --cov=app tests/                        # Tests con cobertura
alembic upgrade head                           # Aplicar migraciones
alembic revision --autogenerate -m "desc"      # Crear migración

# ========== FRONTEND (desde edge_frontend/) ==========
npm run dev                                    # Vite dev server en :5173
npm run type-check                             # TypeScript strict
npm run lint                                   # ESLint
npm test                                       # Vitest
npm run build                                  # Producción → dist/

# ========== DOCKER ==========
docker compose up -d                           # Levantar todos los servicios
docker compose ps                              # Ver estado
docker compose logs -f edge-backend            # Logs del backend
```

---

## 5. Arquitectura

### 5.1 Motor de Escaneo PII

El motor escanea archivos de la red del cliente en busca de datos personales:

1. **Recorre** el árbol de directorios configurado buscando extensiones válidas (PDF, DOCX, XLSX, XLS, DOC, TXT, JPG, PNG, CSV).
2. **Calcula hash MD5** del contenido — si coincide con el hash almacenado, se salta (escaneo incremental).
3. **Extrae texto** vía Apache Tika (incluye OCR para imágenes).
4. **Analiza PII** vía Microsoft Presidio con recognizers ad-hoc para Chile.
5. **Clasifica y cifra**: los hallazgos de categorías sensibles se cifran con AES-256 (Fernet).
6. **Almacena** en MySQL con hash de control para el próximo ciclo.

### 5.2 Entidades Detectadas

| Entidad | Categoría | Almacenamiento | Regex/NLP |
|---|---|---|---|
| `CHILE_RUT` | Básico | Texto plano | `\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b` |
| `EMAIL_ADDRESS` | Básico | Texto plano | Regex estándar |
| `PERSON` | Básico | Texto plano | spaCy NER |
| `PHONE_NUMBER` | Básico | Texto plano | Regex teléfonos chilenos (+56 9/2...) |
| `DATE_TIME` | Básico | Texto plano | Regex fechas (YYYY-MM-DD, DD/MM/YYYY, etc.) |
| `DOMICILIO` | Básico | Texto plano | Regex direcciones (Av., Calle, Pasaje...) + context window |
| `NACIONALIDAD` | Básico | Texto plano | Regex gentilicios + context window |
| `DATA_SALUD` | **Sensible** | 🔒 Cifrado | Regex + context window |
| `DATA_ETNIA` | **Sensible** | 🔒 Cifrado | Regex + context window |
| `DATA_POLITICA` | **Sensible** | 🔒 Cifrado | Regex + context window |
| `DATA_RELIGION` | **Sensible** | 🔒 Cifrado | Regex + context window |
| `DATA_SEXUALIDAD` | **Sensible** | 🔒 Cifrado | Regex + context window |
| `DATA_SINDICAL` | **Sensible** | 🔒 Cifrado | Regex + context window |
| `DATA_SOCIOECONOMICO` | **Sensible** | 🔒 Cifrado | Regex (dinero/hogares) + context window |
| `DATA_IDEOLOGIA` | **Sensible** | 🔒 Cifrado | Regex + context window |
| `DATA_BIOLOGICO` | **Sensible** | 🔒 Cifrado | Regex (ADN/tipos sangre) + context window |
| `DATA_BIOMETRICO` | **Sensible** | 🔒 Cifrado | Regex (huella/hashes dactilares) + context window |
| `DATA_PENAL` | **Sensible** | 🔒 Cifrado | Regex (condena/antecedentes/delitos) + context window |

### 5.3 Context Windows y Lemmatizador Español (Fase 1)

El motor utiliza la sintonización fina de categorías y un booster contextual en bases de datos (extrayendo palabras del nombre de columna) y en archivos.
Para hacerlo robusto, se implementa una **Fase 1 de Lemmatización** en `presidio_service.py` (`stem_word_es`) que:
- Reduce palabras del español a su raíz (eliminando tildes, plurales en `-s`/`-es` y sufijos derivativos como `-acion`, `-idad`, `-ico`, etc.).
- Al arrancar el servicio, expande de manera automática la lista de palabras de contexto (`context`) de cada reconocedor con sus raíces morfológicas calculadas.
- Aplica el stemmer sobre los términos de contexto enviados en las consultas de análisis, garantizando coincidencia con variaciones del lenguaje natural (ej. columnas `afiliaciones_sindicales` o `diagnosticos_medicos` sin tildes).

Las 11 categorías sensibles son:
- **Salud:** paciente, diagnóstico, clínica, hospital, licencia, resultados, tratamiento, enfermedad, patología, etc.
- **Etnia:** conadi, certificado, ascendencia, pueblo, comunidad, beca, etnia, originario.
- **Política:** militante, afiliado, cuota, descuento, planilla, huelga, elecciones, partido.
- **Religión:** bautizo, sacramento, diezmo, iglesia, capellán, religión, fe, obispo.
- **Sexualidad:** orientación, identidad, género, convivencia, transición, diversidad.
- **Sindical:** afiliado, cuota, descuento, huelga, sindicato, gremio, negociacion.
- **Socioeconómico:** quintil, decil, rsh, subsidio, bono, beca, renta, sueldo, salario.
- **Ideología:** convicción, filosofía, ideológica, postura, ecologismo, feminismo.
- **Biológico:** muestra, secuencia, análisis, adn, sangre, rh, grupo.
- **Biométrico:** registro, verificación, autenticación, lector, huella, firma, iris, hash.
- **Penal:** condena, sentencia, antecedentes penales, prontuario, delito, imputado, gendarmería.

Las 2 categorías básicas adicionales (no sensibles, sin cifrado) son:
- **Domicilio:** dirección, calle, avenida, pasaje, comuna, ciudad, región.
- **Nacionalidad:** gentilicios, pasaporte, migración, visa, ciudadanía.

### 5.4 Fase 2 (Transformers) Postergar
La Fase 2 (uso de modelos de Deep Learning tipo spacy-transformers en español) queda **postergada** para preservar la velocidad de escaneo y evitar sobrecarga computacional de RAM/CPU en entornos on-premise locales.
Sin embargo, se dejan plantillas comentadas en `nlp_config.yaml` y `registry.yaml` para habilitarla como opción evolutiva si un cliente lo requiere.

### 5.4 Cifrado

- Algoritmo: AES-256 vía Fernet (librería `cryptography`)
- Llave maestra: env var `PII_ENCRYPTION_KEY` (NUNCA hardcodeada)
- En reposo: datos sensibles cifrados en MySQL
- En tránsito: API descifra al vuelo solo cuando se requiere (DSAR, detalle de hallazgo)

### 5.5 Comunicación con UpShield Central

El Edge Agent reporta a la plataforma central:
- Hallazgos agregados (no datos sensibles en crudo)
- Estado de escaneos
- Heartbeat de salud de servicios

Autenticación: API key del tenant (`UPSHIELD_API_KEY` + `UPSHIELD_TENANT_ID`).
Modo offline-first: si la nube no responde, acumula y reintenta con backoff.

---

## 6. Reglas de dominio que muerden

- **Llave de cifrado NUNCA hardcodeada.** El motor original tiene `LLAVE_MAESTRA = b'zF1o...'` en el código. En el Edge Agent, siempre viene de `PII_ENCRYPTION_KEY` en `.env`.
- **Score >= 0.5 para guardar hallazgo.** Si Presidio retorna un score menor, se descarta.
- **Entidades sensibles = cifradas SIEMPRE.** DATA_SALUD, DATA_ETNIA, DATA_POLITICA, DATA_RELIGION, DATA_SEXUALIDAD, DATA_SINDICAL, DATA_SOCIOECONOMICO, DATA_IDEOLOGIA, DATA_BIOLOGICO, DATA_BIOMETRICO, DATA_PENAL se cifran antes de INSERT.
- **Entidades básicas NUNCA se cifran.** CHILE_RUT, EMAIL_ADDRESS, PERSON, PHONE_NUMBER, DATE_TIME, DOMICILIO, NACIONALIDAD se almacenan en texto plano.
- **Hash incremental es obligatorio.** No re-escanear archivos sin cambios. Compara hash MD5 del contenido.
- **Tika timeout 180s.** Archivos grandes (PDFs de 100+ páginas) pueden tardar.
- **Presidio language = 'es' por defecto con reconocedores ad-hoc adaptables.** El servicio utiliza español (`"es"`) por defecto para el análisis PII. Los reconocedores ad-hoc copian dinámicamente el idioma de análisis solicitado (`"es"` o `"en"`) al enviarse al payload de Presidio Analyzer, garantizando que se ejecuten sobre los modelos cargados (`es_core_news_lg` y `en_core_web_lg`).

---

## 7. Cosas que parecen bugs pero no lo son

**No las "arregles".**

- Los reconocedores de Presidio adaptando dinámicamente el idioma — los reconocedores ad-hoc duplican y establecen el campo `supported_language` al idioma de ejecución de la consulta para poder ser gatillados correctamente por el analizador de Presidio.
- Los archivos `motor_pii.py`, `motor_pii_v2.py`, `motor_pii_v3.py` en la raíz — son versiones anteriores del motor, solo referencia histórica.
- Los archivos `generador_*.py` — son scripts de generación de datos de prueba, no parte del producto.

---

## 8. Entorno

- **Backend:** lee de `.env` en `edge_backend/`.
  - Variables críticas: `DATABASE_URL`, `PII_ENCRYPTION_KEY`, `TIKA_URL`, `PRESIDIO_URL`, `UPSHIELD_API_URL`, `UPSHIELD_API_KEY`, `UPSHIELD_TENANT_ID`
- **Frontend:** lee variables `VITE_*` del `.env` en `edge_frontend/`.
  - Variables críticas: `VITE_API_BASE_URL` (normalmente `http://localhost:8001/api`)
- **Puertos:**
  - Tika: 9998
  - Presidio: 5001
  - Edge Backend: 8001
  - Edge Frontend (dev): 5173
  - Edge Frontend (prod/Nginx): 3000

---

## 9. Flujo de trabajo en Antigravity

### Para tareas simples (≤3 archivos, lógica acotada)
→ Implementa directamente, verifica con checkpoints, actualiza progreso.

### Para tareas complejas (multi-archivo, multi-capa)
1. **Planificar:** Crea `implementation_plan.md`
2. **Esperar aprobación** del usuario
3. **Ejecutar** respetando reglas de §5 y §6
4. **Verificar:** pytest, type-check, lint, checkpoints
5. **Actualizar** progress/current.md y progress/history.md

---

## 10. Antes de declarar `done`

- [ ] Cumples todos los checkpoints aplicables de `CHECKPOINTS.md`
- [ ] `pytest` pasa sin errores nuevos (si tocaste backend)
- [ ] `npm run type-check` y `npm run lint` verdes (si tocaste frontend)
- [ ] Actualizaste `progress/current.md`
- [ ] Añadiste entrada en `progress/history.md`

---

## 11. Cuándo parar y pedir ayuda al humano

- Si `feature_list.json` está vacío o todo en `done`
- Si descubres una regla no documentada aquí
- Si una migración requiere intervención manual
- Si los contenedores Docker fallan al arrancar
- Si encuentras conflicto entre AGENTS.md y el código real
