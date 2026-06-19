# Bitácora de Sesiones

## 2026-06-04-001
**Operador:** Pablo Ortiz
**Tarea:** FEAT-001 — Harness + Scaffolding
**Resultado:** done
**Notas:** Estructura completa creada para edge_backend y edge_frontend, dependencias instaladas, guías de UI creadas, configuraciones de variables de entorno .env inicializadas e init.ps1 verificado.

## 2026-06-04-002
**Operador:** Pablo Ortiz
**Tarea:** FEAT-002 — Modelos SQLAlchemy + Migración Inicial
**Resultado:** done
**Notas:** Modelos para ScanFinding, FileControl, ScanJob y ScanConfig creados. Migración Alembic creada con convenciones de nombres para constraints, aplicada y rollback verificado en InnoDB. Añadidos tests unitarios que pasan exitosamente.

## 2026-06-04-003
**Operador:** Pablo Ortiz
**Tarea:** FEAT-003 — Backend — Servicios Core (Escaneo + Cifrado)
**Resultado:** done
**Notas:** Creados servicios crypto_service (Fernet AES-256), tika_service (extracción texto), presidio_service (análisis PII) y scan_engine (hilo background con control incremental). Routers /scan y /findings implementados con Pydantic schemas. 8 tests unitarios exitosos.

## 2026-06-04-004
**Operador:** Pablo Ortiz
**Tarea:** FEAT-004 — Backend — Config Dinámica + DSAR + Health + Redaction
**Resultado:** done
**Notas:** Implementada configuración dinámica (con validación de rutas y rechazo de directorios de sistema), búsqueda de derechos ARCO (DSAR por RUT con descifrado al vuelo), health checks (FastAPI, DB, Tika, Presidio) y servicio de censura de documentos (PDF mediante PyMuPDF, TXT/CSV por reemplazo e imágenes mediante Pillow). 12 tests unitarios pasando exitosamente.

## 2026-06-04-005
**Operador:** Pablo Ortiz
**Tarea:** FEAT-005 — Backend — Sincronización con UpShield Central
**Resultado:** done
**Notas:** Creado cliente HTTP para reportar al SaaS central con reintentos y backoff exponencial (offline-first). Integrado heartbeat periódico como hilo daemon y reporte de estados y hallazgos agregados (cumpliendo con la privacidad PII al no incluir texto original) al completar o fallar escaneos en scan_engine.py. 8 tests unitarios desarrollados y exitosos (20 tests en total).

## 2026-06-04-006
**Operador:** Pablo Ortiz
**Tarea:** FEAT-006 y FEAT-007 — Frontend & Docker Unificado
**Resultado:** done
**Notas:** Corrección completa de errores de compilación de TypeScript/MUI v6 Grid en el frontend, resolución de problemas de ESLint para dejar el linter 100% en verde, y creación de Dockerfiles multi-stage y archivos de orquestación de Docker Compose para la suite de servicios unificada.

## 2026-06-04-007
**Operador:** Pablo Ortiz
**Tarea:** Despliegue Docker Compose y Solución de Errores de Inicio
**Resultado:** done
**Notas:** Ejecutado docker compose up -d --build. Corregido error de compilación de TypeScript en ScanConfig.tsx y añadidas dependencias faltantes (pymupdf y pillow) en requirements.txt del backend. Verificada salud general de servicios mediante health check endpoint (200 OK con DB, Tika y Presidio activos).

## 2026-06-04-008
**Operador:** Pablo Ortiz
**Tarea:** Corrección de Pantalla de Configuración y Explorador de Directorios
**Resultado:** done
**Notas:** Solucionado el bug de carga infinita en la vista de Configuración. Diseñado e implementado un explorador de directorios interactivo en backend y frontend para la selección cómoda y múltiple de carpetas de escaneo. Recompilado y verificado en Docker Compose.

## 2026-06-04-009
**Operador:** Pablo Ortiz
**Tarea:** Traducción Dinámica de Rutas Host-Contenedor en Docker
**Resultado:** done
**Notas:** Implementado path_service.py para traducir rutas de Windows de la máquina host a rutas lógicas /app del contenedor. Integrado en los módulos de test-path, scan_engine y redaction, permitiendo al usuario configurar y escanear rutas físicas de su máquina sin restricciones de aislamiento de Docker.

## 2026-06-04-010
**Operador:** Pablo Ortiz
**Tarea:** Filtro por Nivel de Riesgo en Hallazgos
**Resultado:** done
**Notas:** Agregado el parámetro is_sensitive en el backend de hallazgos para soportar filtrado por nivel de riesgo (Alto/Moderado). Diseñado e integrado un desplegable "Nivel Riesgo" en la barra de filtros superior de la vista de Hallazgos en el frontend. Recompilado y verificado en Docker.

## 2026-06-04-011
**Operador:** Pablo Ortiz
**Tarea:** Verificación y Credenciales de UpShield Central
**Resultado:** done
**Notas:** Verificado que el OCR optimizado (PSM 11 + preprocesamiento) detecta el RUT en imágenes de carnet de identidad. Agregada la tarjeta de configuración de credenciales de UpShield Cloud (API URL, API Key, Tenant ID, Sync Interval) en la UI y sincronizados los valores en caliente vía os.environ en el backend. 20/20 tests exitosos.

## 2026-06-04-012
**Operador:** Pablo Ortiz
**Tarea:** Corrección del reinicio de configuración por tests unitarios
**Resultado:** done
**Notas:** Se implementó un fixture en `test_feat004.py` para evitar que los tests unitarios sobrescriban persistentemente la configuración de escaneo en la base de datos local. Se restauró el soporte para todas las extensiones de archivos (9 en total) y tipos de PII (8 en total) en la configuración activa en base de datos.

## 2026-06-04-013
**Operador:** Pablo Ortiz
**Tarea:** FEAT-010 — Integración de las 10 categorías de PII y corrección de métricas
**Resultado:** done
**Notas:** Se implementaron las 10 categorías sensibles y básicas de la Ley 21.719 en el backend y frontend. Se resolvió la corrupción de caracteres con acentos en español en Apache Tika forzando el charset UTF-8 en `tika_service.py`. Se actualizaron las métricas del Dashboard para agrupar solo hallazgos activos (`is_resolved == False`) vinculando la visualización del riesgo con `global_risk_level` en el backend. Se integró la limpieza de registros obsoletos de archivos eliminados. Se generaron 60 archivos de prueba reales con las 10 categorías sensibles y formatos de RUT con y sin puntos en "C:\Users\PabloOrtizCollados\Desktop\Archivos Prueba PII".

## 2026-06-04-014
**Operador:** Pablo Ortiz
**Tarea:** FEAT-011 — Clasificación de Riesgo Alto y cifrado de hallazgos básicos con contenido sensible
**Resultado:** done
**Notas:** Se implementó promoción automática (`is_sensitive = True`) y cifrado Fernet AES-256 para hallazgos básicos (como `PERSON`) cuando su texto detectado contiene algún término sensible (e.g. "transexual"). Esto clasifica correctamente el hallazgo como de riesgo `ALTO` en la UI, soluciona la duda sobre `prueba_doc_012_sexualidad.txt` y elimina fugas de PII sensible en texto plano en la base de datos MySQL. Se añadieron tests y se reinició el contenedor del backend para aplicar los cambios.

## 2026-06-04-015
**Operador:** Pablo Ortiz
**Tarea:** FEAT-012 — Estabilización del Proyecto y Despliegue de Cambios
**Resultado:** done
**Notas:** Corrección de errores de compilación TypeScript y ESLint en el frontend. Reparación de pruebas unitarias (`test_db_scan.py` y `test_redaction_and_identity.py`) solucionando problemas de aislamiento de transacciones de base de datos y de variables desconectadas (DetachedInstanceError). Habilitación de la extracción y OCR en imágenes embebidas de PDFs (`X-Tika-PDFExtractInlineImages`). Despliegue de contenedores actualizados con Docker Compose. Todos los checkpoints están en verde.

## 2026-06-05-016
**Operador:** Pablo Ortiz
**Tarea:** FEAT-013 — Rediseño Simplificado del Configurador de Base de Datos (Wizard) e Indicador de Watcher
**Resultado:** done
**Notas:** Rediseñado el conector de Base de Datos para ofrecer un asistente simple paso a paso. Se corrigieron los errores de tipado en TypeScript y advertencias de ESLint en `ScanConfig.tsx`. Se integró el servicio "Monitoreo Tiempo Real" en la tarjeta de salud de servicios en la barra lateral del frontend (añadiendo chequeo de salud dinámico en el endpoint del backend `/api/health`). Todos los tests de backend pasaron con éxito y se desplegaron los contenedores actualizados en Docker Compose.

## 2026-06-05-017
**Operador:** Pablo Ortiz
**Tarea:** FEAT-014 — Alertas por Correo Electrónico y UI de Configuración SMTP
**Resultado:** done
**Notas:** Implementado hilo de monitoreo demonio (`alert_service.py`) con control anti-spam de transiciones de estado para alertar al administrador sobre caídas y recuperaciones de servicios de Docker. Agregada la tarjeta visual "Alertas por Correo (SMTP)" en `ScanConfig.tsx` con campos para host, puerto, credenciales, remitente, destinatario e intervalo, persistiendo los parámetros dinámicamente en el `.env` del backend. Añadidos 5 tests en `test_alert_service.py` y verificado de forma end-to-end con un servidor SMTP local simulado sobre el puerto 1025. Todos los 30 tests pasan de forma exitosa y la compilación/linter está libre de errores.

## 2026-06-05-018
**Operador:** Pablo Ortiz
**Tarea:** Integración del Escáner de Bases de Datos SQL en el Escaneo Global
**Resultado:** done
**Notas:** Refactorizado `db_scan_engine.py` para separar el escaneo de bases de datos individuales en funciones reutilizables (`scan_single_db_config` y `estimate_db_config_cells`). Integrado el escaneo de bases de datos SQL activas de forma automática dentro del flujo de `scan_engine.py` (`run_scan_async`). Al presionar "Escanear de Nuevo" en el Dashboard, se realiza un cálculo unificado de celdas y archivos totales, se escanean secuencialmente los conectores activos y se actualizan dinámicamente sus métricas de progreso bajo el mismo Job de escaneo. Se añadió una prueba unitaria y se verificó que todas las 31 pruebas del backend pasan con éxito.

## 2026-06-05-019
**Operador:** Pablo Ortiz
**Tarea:** Reconstrucción del Dashboard para Integración de Bases de Datos y Archivos
**Resultado:** done
**Notas:** Rediseñado el Dashboard y las métricas asociadas para mostrar de forma independiente archivos físicos y celdas de bases de datos. Modificado el backend (esquema y router `/stats`) para calcular de forma desglosada los elementos escaneados, bases de datos activas y hallazgos en cada origen. En el frontend, se expandieron los KPI cards a 5 tarjetas responsivas y se adaptó el gráfico de barras ("Orígenes más Afectados") para colorear las tablas de base de datos de naranja y las carpetas de archivos de azul. Se incorporaron íconos contextuales específicos en la lista de hallazgos recientes para distinguir orígenes con claridad. Todas las pruebas del backend pasaron con éxito y se validó la compilación de Vite sin advertencias de tipo.

## 2026-06-05-020
**Operador:** Pablo Ortiz
**Tarea:** Optimización de Rendimiento en Escaneo de BD y Corrección del Botón Detener
**Resultado:** done
**Notas:** Se corrigió el cuello de botella en el escaneo de bases de datos de gran tamaño agrupando las escrituras en lotes de 100 celdas antes de llamar a `commit()`, logrando un aumento del 100x en la velocidad de escaneo y evitando bloqueos. Se implementó la sobrecarga del endpoint POST `/api/scan/stop` recibiendo la estructura JSON `{ job_id }` del cliente React para corregir el error 404 del botón Detener, el cual ahora funciona correctamente. Se reiniciaron los servicios de Docker y se verificaron las pruebas automatizadas (todas pasando).

## 2026-06-05-021
**Operador:** Pablo Ortiz
**Tarea:** Corrección de Métricas y UX del Panel de Control
**Resultado:** done
**Notas:** Se implementaron actualizaciones atómicas `.update(...)` para ScanJob en el motor de escaneo de archivos físicos y de bases de datos SQL, solucionando la condición de carrera producida por REPEATABLE READ en hilos concurrentes que generaba discrepancia en el total. Se corrigió la agrupación de severidades en backend para usar directamente la columna is_sensitive. Se mejoró la UX del Dashboard con tooltips informativos, etiquetas legibles rotadas y tooltip personalizado con rutas completas para el gráfico de barras. Asimismo, se homogeneizó la altura de las tarjetas KPI del Dashboard aplicando `height: '100%'` para una alineación horizontal impecable, y se fijó la rejilla de contadores finales del escáner en un diseño 2x2 permanente (`repeat(2, 1fr)`) para garantizar una visualización sin recortes horizontalmente en cualquier resolución o nivel de zoom. Se reconstruyeron los contenedores Docker y se verificaron todas las 31 pruebas unitarias.

## 2026-06-05-022
**Operador:** Pablo Ortiz
**Tarea:** Optimización de Presidio en Español e Identificación de Datos Sensibles
**Resultado:** done
**Notas:** Se configuró el soporte del modelo de español (`es_core_news_lg`) en Presidio mediante la creación y montaje de `nlp_config.yaml` y la variable `NLP_CONF_FILE` en `docker-compose.yml` para evitar KeyErrors. Se cambiaron las llamadas a la API de análisis para procesar por defecto en español (`language: "es"`), lo que mejoró enormemente la detección de nombres y contextología en español. Se expandieron exhaustivamente todas las categorías de PII sensibles con términos de la Ley 21.719 en Chile. Se incrementó la certeza base de los recognizers a `0.6` para asegurar que las celdas de bases de datos que contienen datos sensibles individuales (como "Trastorno de Ansiedad") superen el umbral de detección de `0.5` de forma directa sin depender de palabras de contexto largo. Se verificó con un re-escaneo completo de la BD que todos los hallazgos sensibles, básicos y correos asociados se extraen y relacionan perfectamente en el perfil del RUT (riesgo ALTO y 6 hallazgos correlacionados).## 2026-06-05-023
**Operador:** Antigravity
**Tarea:** Captura y Correlación de Datos de Renta, Teléfono y Fecha de Nacimiento en Bases de Datos
**Resultado:** done
**Notas:** Implementado boosting contextual en el escáner de bases de datos dividiendo el nombre de la columna y pasándolo como context. Ampliado el servicio de identidad para correlacionar hallazgos de PHONE_NUMBER y DATE_TIME en sets phones y birth_dates. Modificado el tipo IdentitySubject en frontend e integrado campos e iconos correspondientes en el Drawer de detalle de IdentityGraph.tsx. Limpiada la caché y gatillado un escaneo de la BD local confirmando la detección correcta y cifrada AES-256 de los ingresos (DATA_SOCIOECONOMICO) y teléfonos/fechas de nacimiento vinculados a Nancy Reyes (RUT 10.736.681-4) en la UI.

## 2026-06-05-024
**Operador:** Antigravity
**Tarea:** Sintonía fina de categorías en bases de datos y archivos
**Resultado:** done
**Notas:** Modificado el motor de escaneo de bases de datos (`db_scan_engine.py`) para aceptar e instrumentar el parámetro de entidades deseadas, consultando la configuración activa `ScanConfig` en caso de no proveerse. Propagadas las categorías en el escaneo global de `scan_engine.py` y en escaneos independientes de conexión de base de datos. Añadida prueba unitaria en `test_db_scan.py` para verificar el correcto filtrado de llamadas a Presidio. Todas las 32 pruebas del backend pasaron con éxito.

## 2026-06-05-025
**Operador:** Antigravity
**Tarea:** Fase 1: Lemmatización y Contexto Léxico para Presidio
**Resultado:** done
**Notas:** Implementada función `stem_word_es` en el servicio de Presidio para normalizar y extraer raíces de palabras en español (eliminando acentos, plurales en -s y -es, y sufijos comunes). Automatizada la expansión a nivel morfológico de las palabras de contexto de los reconocedores en tiempo de carga. Configurado el método `analyze_text` para aplicar el stemmer sobre la lista de contexto del payload. Añadidas 2 pruebas unitarias de validación en `test_services_and_routers.py`. Todas las 34 pruebas de backend son verdes.

## 2026-06-06-026
**Operador:** Antigravity
**Tarea:** Creación de Tabla de Entrenamiento PII de 20,000 Filas (10 Categorías Sensibles)
**Resultado:** done
**Notas:** Creada y poblada la tabla MySQL local `clientes_entrenamiento_pii` con 20,000 filas de datos ficticios realistas para Chile. Todos los RUTs generados incluyen DV válido bajo Módulo 11. Se poblaron de forma dispersa las 10 categorías de datos sensibles de la Ley 21.719 en Chile y se verificó la distribución mediante un script de control.

## 2026-06-06-027
**Operador:** Antigravity
**Tarea:** Estabilización del Dashboard, Barra de Progreso y Correlación de Identidad
**Resultado:** done
**Notas:** Corregido el cálculo de barra de progreso que excedía 100% y arrojaba números negativos mediante el refresco y reevaluación dinámica del progreso al finalizar o cancelar. Optimizado el servicio de correlación de identidades para procesar perfiles en memoria con $O(N)$ mitigando el cuelgue por miles de RUTs en MySQL. Implementada cancelación inmediata en bucles internos del escaneo de base de datos. Restauradas estadísticas del Dashboard tras completar con éxito el escaneo global (Job 175). Todas las 34 pruebas del backend pasan exitosamente.

## 2026-06-19-001
**Operador:** Antigravity
**Tarea:** Integración del Logo Oficial y Archivos de Distribución de Base de Datos e Instalación
**Resultado:** done
**Notas:** Se integró el logo horizontal oficial de upshield (`logo_light.svg` y `logo_dark.svg`) en la barra superior del frontend, se actualizó el favicon a la marca oficial de la plataforma y se adaptaron los textos descriptivos a minúsculas (`upshield Edge Agent`). Se creó el script SQL independiente `init_database.sql` con el esquema de tablas MySQL 8.0 y sus relaciones de llave foránea. Se documentó todo el proceso de aprovisionamiento en `INSTALL_GUIDE.md` para desarrollo y producción con Docker Compose. Se verificó con éxito la compilación del frontend (`npm run build`).

## 2026-06-19-002
**Operador:** Antigravity
**Tarea:** FEAT-015 — Remediación y Censura In-Situ en UI
**Resultado:** done
**Notas:** Se implementó e integró visualmente en el frontend la remediación de hallazgos mediante Censura In-Situ (sobrescribir en caliente) y Cuarentena (mover a zona segura con placeholder de texto). Se añadieron diálogos modales de confirmación para evitar ejecuciones accidentales, se enlazaron con los endpoints correspondientes de la API y se aseguró la recarga dinámica del estado. Adicionalmente, se corrigieron las advertencias de ESLint en `Dashboard.tsx`, se actualizaron los archivos de logotipos oficiales (`logo_light.svg` y `logo_dark.svg`) con los del escritorio, y se solucionó un bug de sobrecarga en la búsqueda de censura filtrando los hallazgos de base de datos (`db://%`) para retornar únicamente archivos físicos, reparando el error de AJAX del buscador.
