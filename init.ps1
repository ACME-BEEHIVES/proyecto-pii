# Para colorear la consola en Windows
$colors = @{
    Reset = "`e[0m"
    Bold = "`e[1m"
    Red = "`e[31m"
    Green = "`e[32m"
    Yellow = "`e[33m"
    Blue = "`e[34m"
    Magenta = "`e[35m"
    Cyan = "`e[36m"
    White = "`e[37m"
}

function Write-Bold ($text) { Write-Host "$($colors.Bold)$text$($colors.Reset)" }
function Write-OK ($text) { Write-Host "$($colors.Green)[ OK ] $text$($colors.Reset)" }
function Write-Warn ($text) { Write-Host "$($colors.Yellow)[WARN] $text$($colors.Reset)" }
function Write-Fail ($text) { Write-Host "$($colors.Red)[FAIL] $text$($colors.Reset)" }
function Write-Info ($text) { Write-Host "$($colors.Cyan)[INFO] $text$($colors.Reset)" }

Write-Bold "===================================================="
Write-Bold "  UpShield Edge Agent - Entorno de Desarrollo"
Write-Bold "===================================================="
Write-Host ""

# Seccion 1: Herramientas del sistema
Write-Bold "--- Sección 1: Herramientas del Sistema ---"
$tools = @("python", "pip", "node", "npm", "git", "docker")
foreach ($tool in $tools) {
    if (Get-Command $tool -ErrorAction SilentlyContinue) {
        $version = ""
        if ($tool -eq "python") { $version = (python --version 2>&1) }
        elseif ($tool -eq "node") { $version = (node --version 2>&1) }
        elseif ($tool -eq "docker") { $version = "instalado" }
        else { $version = "disponible" }
        Write-OK "$($tool) está listo ($version)"
    } else {
        Write-Warn "$($tool) no está en el PATH. Algunas tareas podrían requerirlo."
    }
}
Write-Host ""

# Seccion 2: Estructura del harness
Write-Bold "--- Sección 2: Estructura del Harness ---"
$harnessFiles = @("AGENTS.md", "CHECKPOINTS.md", "feature_list.json", "progress/current.md", "progress/history.md")
foreach ($file in $harnessFiles) {
    if (Test-Path $file) {
        Write-OK "Archivo de control detectado: $file"
    } else {
        Write-Fail "Falta archivo de control: $file"
    }
}
Write-Host ""

# Seccion 3: Estructura del proyecto
Write-Bold "--- Sección 3: Estructura del Proyecto ---"
$projectPaths = @(
    "edge_backend/app/main.py",
    "edge_backend/requirements.txt",
    "edge_frontend/package.json",
    "edge_frontend/src/App.tsx"
)
foreach ($path in $projectPaths) {
    if (Test-Path $path) {
        Write-OK "Ruta del proyecto detectada: $path"
    } else {
        Write-Fail "Falta archivo o carpeta crítica: $path"
    }
}
Write-Host ""

# Seccion 4: Archivos de configuracion
Write-Bold "--- Sección 4: Configuración (.env) ---"
$backendEnv = "edge_backend/.env"
$frontendEnv = "edge_frontend/.env"

if (Test-Path $backendEnv) {
    Write-OK "Configuración backend .env existe."
} else {
    Write-Warn "Falta edge_backend/.env. Creando uno inicial desde .env.example..."
    if (Test-Path "edge_backend/.env.example") {
        Copy-Item "edge_backend/.env.example" $backendEnv
        Write-OK "Inicializado edge_backend/.env"
    } else {
        Write-Fail "No se pudo crear .env porque no existe .env.example"
    }
}

if (Test-Path $frontendEnv) {
    Write-OK "Configuración frontend .env existe."
} else {
    Write-Warn "Falta edge_frontend/.env. Creando uno inicial..."
    "VITE_API_BASE_URL=http://localhost:8001/api" | Out-File -FilePath $frontendEnv -Encoding utf8
    Write-OK "Inicializado edge_frontend/.env con VITE_API_BASE_URL"
}
Write-Host ""

# Seccion 5: Contenedores docker
Write-Bold "--- Sección 5: Servicios Docker (Tika + Presidio) ---"
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $runningContainers = docker ps --format '{{.Names}}'
    $containersToCheck = @("tika", "presidio")
    foreach ($c in $containersToCheck) {
        $found = $false
        foreach ($rc in $runningContainers) {
            if ($rc -like "*$c*") {
                $found = $true
                break
            }
        }
        if ($found) {
            Write-OK "Contenedor docker running: $c"
        } else {
            Write-Warn "Contenedor $c no parece estar corriendo. Ejecuta 'docker compose up -d'"
        }
    }
} else {
    Write-Warn "No se pudo verificar docker porque no está disponible."
}
Write-Host ""

# Seccion 6: Estado del proyecto
Write-Bold "--- Sección 6: Estado del Proyecto ---"
if (Test-Path "progress/current.md") {
    $current = Get-Content "progress/current.md" -Raw
    Write-Host $current
} else {
    Write-Fail "No se pudo leer progress/current.md"
}
Write-Host ""

Write-Bold "--- Sección 7: Próximos Pasos ---"
Write-Info "1. Si falta correr docker: docker compose up -d"
Write-Info "2. Backend: cd edge_backend; uvicorn app.main:app --reload --port 8001"
Write-Info "3. Frontend: cd edge_frontend; npm run dev"
Write-Bold "===================================================="
