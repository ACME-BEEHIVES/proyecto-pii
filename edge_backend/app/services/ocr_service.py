"""
ocr_service.py — Motor de extracción de texto con PaddleOCR (reemplaza Apache Tika + Tesseract).

Soporta:
  - PDF nativo (texto seleccionable): extracción directa con pymupdf, 0.1 s/pág
  - PDF escaneado (imagen):          pymupdf renderiza páginas → PaddleOCR, ~2–3 s/pág
  - Imágenes (JPG, PNG):             PaddleOCR directo
  - DOCX/DOC:                        python-docx
  - XLSX/XLS:                        openpyxl + xlrd
  - TXT/CSV:                         lectura directa UTF-8
"""

import os
import logging
from functools import lru_cache

logger = logging.getLogger("ocr_service")

# ---------------------------------------------------------------------------
# Inicialización lazy de PaddleOCR (se carga al primer uso, no al importar)
# ---------------------------------------------------------------------------
_paddle_instance = None

def _get_paddle():
    """Retorna la instancia singleton de PaddleOCR, inicializando si es necesario."""
    global _paddle_instance
    if _paddle_instance is None:
        try:
            from paddleocr import PaddleOCR
            logger.info("Inicializando PaddleOCR (primera vez, descarga de modelos)...")
            _paddle_instance = PaddleOCR(
                use_angle_cls=True,   # Detecta texto rotado (carnets, escaneos torcidos)
                lang="es",            # Español como idioma principal
                use_gpu=False,        # CPU-only (on-premise sin GPU)
                enable_mkldnn=True,   # Aceleración Intel MKL-DNN (más rápido en CPUs modernas)
            )
            logger.info("PaddleOCR listo.")
        except Exception as e:
            logger.error(f"No se pudo inicializar PaddleOCR: {e}")
            raise
    return _paddle_instance


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _ocr_image_array(img_array) -> str:
    """Ejecuta PaddleOCR sobre un array de imagen NumPy y retorna el texto."""
    paddle = _get_paddle()
    result = paddle.ocr(img_array, cls=True)
    if not result or not result[0]:
        return ""
    lines = []
    for line in result[0]:
        if line and len(line) >= 2:
            text, confidence = line[1]
            if confidence >= 0.5:  # Descartar ruido de baja confianza
                lines.append(text)
    return "\n".join(lines)


def _extract_pdf(file_path: str) -> str:
    """
    Extrae texto de PDF usando pymupdf.
    - Si la página tiene texto seleccionable → extracción directa (0.05 s/pág).
    - Si la página es una imagen → la renderiza y pasa a PaddleOCR (~2 s/pág).
    """
    import fitz  # pymupdf
    import numpy as np
    from PIL import Image
    import io

    doc = fitz.open(file_path)
    all_text = []

    for page_num, page in enumerate(doc):
        # Intentar extracción nativa primero
        native_text = page.get_text("text").strip()

        if len(native_text) >= 20:
            # Página con texto nativo — rapidísimo
            all_text.append(native_text)
        else:
            # Página escaneada — renderizar a imagen y aplicar OCR
            try:
                # Renderizar a 200 DPI (balance calidad/velocidad para PaddleOCR)
                mat = fitz.Matrix(200 / 72, 200 / 72)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img_data = pix.tobytes("png")

                img = Image.open(io.BytesIO(img_data)).convert("RGB")
                img_array = np.array(img)

                ocr_text = _ocr_image_array(img_array)
                if ocr_text:
                    all_text.append(ocr_text)
                    logger.debug(f"PaddleOCR pág {page_num+1}: {len(ocr_text)} chars")
            except Exception as e:
                logger.warning(f"Error OCR pág {page_num+1} de {file_path}: {e}")

    doc.close()
    return "\n\n".join(all_text)


def _extract_image(file_path: str) -> str:
    """Extrae texto de una imagen JPG/PNG usando PaddleOCR."""
    import numpy as np
    from PIL import Image

    img = Image.open(file_path).convert("RGB")
    img_array = np.array(img)
    return _ocr_image_array(img_array)


def _extract_docx(file_path: str) -> str:
    """Extrae texto de un archivo DOCX usando python-docx."""
    from docx import Document
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    # También extraer texto de tablas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    paragraphs.append(cell.text.strip())
    return "\n".join(paragraphs)


def _extract_xlsx(file_path: str) -> str:
    """Extrae texto de XLSX usando openpyxl."""
    import openpyxl
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    rows = []
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(values_only=True):
            row_text = " | ".join(str(v) for v in row if v is not None and str(v).strip())
            if row_text:
                rows.append(row_text)
    wb.close()
    return "\n".join(rows)


def _extract_xls(file_path: str) -> str:
    """Extrae texto de XLS usando xlrd."""
    import xlrd
    wb = xlrd.open_workbook(file_path)
    rows = []
    for sheet in wb.sheets():
        for rx in range(sheet.nrows):
            row_text = " | ".join(
                str(v) for v in sheet.row_values(rx) if str(v).strip()
            )
            if row_text:
                rows.append(row_text)
    return "\n".join(rows)


def _extract_txt(file_path: str) -> str:
    """Lee un archivo de texto plano o CSV."""
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(file_path, "r", encoding=enc, errors="ignore") as f:
                return f.read()
        except Exception:
            continue
    return ""


# ---------------------------------------------------------------------------
# API pública (misma interfaz que el antiguo tika_service)
# ---------------------------------------------------------------------------

def extract_text(file_path: str) -> str:
    """
    Punto de entrada principal. Detecta el tipo de archivo y extrae el texto.
    Compatible con la interfaz anterior de tika_service.extract_text().
    """
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            return _extract_pdf(file_path)
        elif ext in (".jpg", ".jpeg", ".png"):
            return _extract_image(file_path)
        elif ext in (".docx",):
            return _extract_docx(file_path)
        elif ext in (".doc",):
            # Intentar con python-docx primero, fallback a lectura binaria
            try:
                return _extract_docx(file_path)
            except Exception:
                return _extract_txt(file_path)
        elif ext in (".xlsx",):
            return _extract_xlsx(file_path)
        elif ext in (".xls",):
            return _extract_xls(file_path)
        elif ext in (".txt", ".csv", ".odt", ".ods"):
            return _extract_txt(file_path)
        else:
            # Tipo desconocido — intentar como texto plano
            return _extract_txt(file_path)
    except Exception as e:
        raise Exception(f"Error extrayendo texto de {os.path.basename(file_path)}: {e}")


def check_health() -> bool:
    """
    Verifica que el motor de OCR está operativo verificando que la librería
    está instalada. No inicializa los modelos para no bloquear el health check.
    """
    try:
        import paddleocr  # noqa: F401
        import fitz       # noqa: F401
        return True
    except ImportError:
        return False
