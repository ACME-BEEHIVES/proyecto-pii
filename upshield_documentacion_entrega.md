# upshield: Documentación de Traspaso Técnico y Roadmap Estratégico

Este documento detalla el estado actual del MVP de **upshield**, su arquitectura técnica, y las especificaciones para la siguiente fase de desarrollo a cargo del equipo de Antigravity.

---

## 1. Visión General del Proyecto
**upshield** es una plataforma de descubrimiento y protección de datos sensibles (DLP) diseñada para el cumplimiento de la **Ley 21.719 (Chile)**. Su arquitectura es **híbrida/Edge**: el motor de procesamiento reside en las instalaciones del cliente (On-Premise) para garantizar la privacidad, mientras que la gestión se centraliza en un dashboard ejecutivo.

---

## 2. Arquitectura Técnica del MVP (Estado Actual)

El sistema actual es funcional y consta de un motor de escaneo incremental con las siguientes capacidades:

### A. Extracción Multiformato (Apache Tika)
Utiliza un contenedor de **Apache Tika** para la extracción de texto en:
- Documentos de oficina (PDF, DOCX, XLSX).
- Imágenes (JPG, PNG) mediante OCR.
- Archivos de texto plano (TXT, CSV).

### B. Motor de Análisis PII (Microsoft Presidio)
Implementa lógica de NLP para identificar:
- **Datos Básicos:** RUT chileno (Regex validado) y correos electrónicos.
- **Matriz de Datos Sensibles (Ley 21.719):** Clasificación por Salud, Etnia, Política/Sindical, Religión y Sexualidad.

### C. Lógica de Contexto (Context Window)
Se implementó una solución para el límite de memoria de la IA (5 tokens). El motor utiliza "palabras puente" (ej. "positivo", "militante", "conadi") para asegurar que el dato sensible se clasifique correctamente incluso con palabras de relleno.

---

## 3. Seguridad y Cifrado de Datos

upshield aplica el principio de **Seguridad por Diseño**:

- **Cifrado Simétrico (AES-256):** Los hallazgos de categorías sensibles se encriptan mediante la librería `cryptography` (Fernet) antes de ser guardados en MySQL.
- **Dato en Reposo:** En la base de datos, la información sensible es indescifrable sin la llave maestra.
- **Dato en Tránsito:** La API realiza un **enmascaramiento automático** (Data Masking) para reportes de auditoría (ej. `b*****a`).

---

## 4. API Edge y Módulo DSAR

Se desarrolló una API basada en **FastAPI** que corre localmente en el cliente:
- **Endpoint `GET /api/v1/dsar/{rut}`:** Permite realizar un mapeo instantáneo de todos los documentos que contienen información de un titular específico.
- **Mapeo de Datos:** Cruza el RUT encontrado con otros datos sensibles en los mismos archivos para generar el informe de Derechos ARCO.

---

## 5. Especificaciones para Antigravity (Roadmap)

Se requiere que el equipo de desarrollo implemente los siguientes módulos para completar el producto SaaS:

### A. Módulo de Configuración Dinámica
- **Objetivo:** Eliminar la intervención del código para cambiar rutas de red.
- **Requerimiento:** Crear una interfaz UI que escriba en una tabla `config_escaneo`. El motor de Python debe leer esta tabla en cada ciclo de ejecución.

### B. Dashboard Ejecutivo y Reportabilidad
- **Visualización:** Gráficos de distribución de riesgo por categoría legal.
- **KPIs:** Volumen de datos expuestos, nivel de riesgo por departamento, y cumplimiento de plazos DSAR.

### C. Motor de Censura (Redaction Engine)
- **Funcionalidad:** Generar copias de los archivos originales donde la información sensible esté ofuscada visualmente (rectángulos negros) para su compartición segura.

### D. Monitor de Salud del Sistema (Observabilidad)
- **Heartbeat:** Implementar chequeos de estado (`/health`) para los contenedores de Tika y Presidio.
- **Alertas:** Notificación inmediata al Dashboard central si algún servicio local se detiene.

---

## 6. Stack Tecnológico Utilizado
- **Lenguaje:** Python 3.10+
- **Framework API:** FastAPI / Uvicorn
- **Extracción:** Apache Tika (Docker)
- **Análisis:** Microsoft Presidio (Docker)
- **Base de Datos:** MySQL 8.0
- **Criptografía:** AES-256 (Fernet)

---

**Preparado por:** Pablo Ortiz - Senior Consultant | upshield AI
**Fecha de Entrega:** 18 de Abril, 2026
