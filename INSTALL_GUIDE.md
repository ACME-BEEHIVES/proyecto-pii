# Guía de Instalación — UpShield Edge Agent

El **UpShield Edge Agent** es el componente local (on-premise) diseñado para escanear y proteger datos personales (PII) dentro de la infraestructura del cliente bajo la **Ley 21.719 (Chile)**. Este agente se comunica de forma segura con la plataforma central de UpShield.

Esta guía detalla la configuración y despliegue del agente en dos escenarios:
1. **Desarrollo (Desde Código Fuente)**: Para transferencias de código o integraciones personalizadas.
2. **Producción (Docker Compose)**: Para instalación y despliegue rápido en clientes.

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
- **Docker y Docker Compose** (Recomendado para producción y desarrollo).
- **MySQL 8.0** (Instancia local o en la red del cliente).
- **Python 3.12** y **Node.js 18+** (Solo si ejecutas desde el código fuente).

---

## 1. Configuración de Base de Datos

El agente requiere una base de datos MySQL con el esquema `pii_discovery`.

1. Conéctate a tu base de datos MySQL e inicializa las tablas ejecutando el script `init_database.sql`:
   ```bash
   mysql -u root -p < init_database.sql
   ```
   *Nota: Este script creará la base de datos `pii_discovery` y las 5 tablas necesarias (`scan_jobs`, `control_archivos`, `hallazgos`, `scan_configs`, `db_configs`) con sus índices y relaciones.*

---

## 2. Variables de Entorno (.env)

En la raíz de la carpeta `edge_backend/`, crea un archivo `.env` tomando como base `edge_backend/.env.example`.

### Variables Críticas

| Variable | Descripción | Ejemplo / Valor Recomendado |
|---|---|---|
| `DATABASE_URL` | URL de conexión a MySQL | `mysql+pymysql://root:password@localhost:3306/pii_discovery` |
| `PII_ENCRYPTION_KEY` | Llave AES-256 para cifrar PII sensible | Generar usando Fernet (ver instrucción abajo) |
| `TIKA_URL` | Endpoint del servicio de extracción Apache Tika | `http://localhost:9998/tika` |
| `PRESIDIO_URL` | Endpoint del servicio analizador Presidio | `http://localhost:5001/analyze` |
| `UPSHIELD_API_URL` | Endpoint de la plataforma central UpShield | `https://api.upshield.cl/v1` |
| `UPSHIELD_API_KEY` | Llave API de autenticación en la nube | *Provista por la consola central* |
| `UPSHIELD_TENANT_ID` | Identificador del cliente | *Provisto por la consola central* |

### Cómo generar la `PII_ENCRYPTION_KEY`
Ejecuta el siguiente comando en tu terminal para obtener una llave válida:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Copia el resultado y asígnalo a la variable `PII_ENCRYPTION_KEY` en tu `.env`. **Nunca compartas esta llave, ya que cifra los hallazgos en reposo.**

---

## 3. Escenario A: Despliegue en Desarrollo (Desde Código Fuente)

Este escenario es útil para depurar el agente o trabajar directamente sobre su código.

### Paso 1: Levantar servicios auxiliares (Tika & Presidio)
Usa Docker para levantar los motores de extracción y análisis PII:
```bash
docker compose up -d tika presidio-analyzer
```

### Paso 2: Configurar y Ejecutar el Backend (FastAPI)
1. Navega al directorio del backend:
   ```bash
   cd edge_backend
   ```
2. Crea e inicia un entorno virtual de Python:
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En macOS/Linux:
   source venv/bin/activate
   ```
3. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta el servidor FastAPI con hot-reload en el puerto 8001:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

### Paso 3: Configurar y Ejecutar el Frontend (React + Vite)
1. Abre otra terminal y navega al directorio del frontend:
   ```bash
   cd edge_frontend
   ```
2. Crea el archivo `.env` en la raíz de `edge_frontend/`:
   ```env
   VITE_API_BASE_URL=http://localhost:8001/api
   ```
3. Instala los paquetes de npm:
   ```bash
   npm install
   ```
4. Inicia el servidor de desarrollo de Vite:
   ```bash
   npm run dev
   ```
5. Abre en tu navegador la dirección indicada (por defecto `http://localhost:5173`).

---

## 4. Escenario B: Despliegue en Producción (Docker Compose Unificado)

Para desplegar en el cliente final de forma aislada y optimizada, se utiliza un único comando de Docker Compose que orquesta los 4 servicios.

1. Asegúrate de configurar las variables de entorno en el archivo `.env` de la raíz del proyecto.
2. Inicia todos los contenedores en segundo plano:
   ```bash
   docker compose up -d
   ```
3. Verifica que los 4 servicios estén corriendo correctamente:
   ```bash
   docker compose ps
   ```
   Deberías ver:
   - `edge-frontend` (Puerto 3000, servido por Nginx y redireccionando las peticiones de API al backend).
   - `edge-backend` (Puerto 8001).
   - `tika` (Puerto 9998).
   - `presidio-analyzer` (Puerto 5001).

4. Accede a la plataforma web a través de `http://localhost:3000`.

---

## 5. Verificación de Funcionamiento

Una vez que la aplicación esté corriendo (desarrollo o producción):

1. **Estado de los Servicios**: En el panel lateral izquierdo de la interfaz, el widget de salud de servicios debe mostrar luz verde (Conectado) para **Tika**, **Presidio** y la base de datos MySQL.
2. **Ejecutar Escaneo de Prueba**:
   - Ve a la pestaña **Configuración**.
   - Ingresa una ruta de prueba que contenga archivos de interés (ej. `.pdf`, `.png`, `.docx`).
   - Haz clic en **Guardar Configuración**.
   - Haz clic en **Iniciar Escaneo** en la esquina superior derecha del Dashboard.
   - Revisa en tiempo real el avance y valida la aparición de los hallazgos en la pestaña **Hallazgos PII**.
3. **Prueba de Cifrado**: Conéctate directamente a MySQL mediante CLI o un cliente visual (DBeaver, phpMyAdmin, etc.) y ejecuta:
   ```sql
   SELECT texto_detectado, tipo_entidad FROM hallazgos WHERE tipo_entidad LIKE 'DATA_%';
   ```
   Verifica que para las entidades sensibles (Salud, Etnia, Política, Religión, Sexualidad) el valor del texto detectado se guarde en formato cifrado (comienza por una cadena Fernet legible como `gAAAAA...`), mientras que las básicas (RUT, Nombre, Email) se guarden en texto plano.
