import os
import logging
import requests
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("tika_service")


def _extract_text_image_direct(file_path: str) -> str:
    """
    Pipeline OCR optimizado para imágenes (JPG, PNG).
    Usa múltiples pasadas con distintas estrategias de pre-procesamiento
    y combina los resultados para maximizar la extracción de texto.
    Optimizado para documentos de identidad, formularios y fotos de documentos.
    """
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    import pytesseract

    img = Image.open(file_path)
    img_gray = img.convert("L")

    # Redimensionar a un ancho grande para mejor resolución OCR
    w, h = img_gray.size
    target_width = 2500
    if w < target_width:
        scale = target_width / w
        img_gray = img_gray.resize(
            (int(w * scale), int(h * scale)), Image.LANCZOS
        )

    # --- Multi-pass: ejecutar varias estrategias y combinar el texto ---
    strategies = [
        # (nombre, función de transformación)
        ("contraste", lambda i: ImageEnhance.Contrast(i).enhance(2.5)),
        ("invertida", lambda i: ImageEnhance.Contrast(ImageOps.invert(i)).enhance(2.0)),
        ("autocontraste", lambda i: ImageOps.autocontrast(i, cutoff=5)),
        ("nitidez", lambda i: ImageEnhance.Sharpness(
            ImageEnhance.Contrast(i).enhance(1.5)
        ).enhance(3.0)),
        ("binarizada", lambda i: ImageEnhance.Contrast(i).enhance(2.0).point(
            lambda x: 255 if x > 140 else 0, "1"
        ).convert("L").filter(ImageFilter.MedianFilter(size=3))),
    ]

    best_text = ""
    all_texts = []

    for name, transform in strategies:
        try:
            img_processed = transform(img_gray)
        except Exception:
            continue

        # Probar 2 modos PSM por estrategia
        for psm in [6, 3]:
            try:
                config = f"--psm {psm} --oem 3 -l spa+eng"
                text = pytesseract.image_to_string(img_processed, config=config)
                text_clean = text.strip()
                if text_clean:
                    all_texts.append(text_clean)
                    if len(text_clean) > len(best_text):
                        best_text = text_clean
            except Exception as e:
                logger.debug(f"OCR {name} psm={psm} falló: {e}")

    # Combinar: usar el texto más largo como base, y agregar líneas únicas de otros
    if not all_texts:
        return ""

    # Extraer líneas únicas de todos los resultados
    seen_lines = set()
    combined_lines = []

    # Primero agregar todas las líneas del mejor resultado
    for line in best_text.split("\n"):
        line_clean = line.strip()
        if line_clean and len(line_clean) >= 2:
            normalized = "".join(c for c in line_clean.lower() if c.isalnum())
            if normalized and normalized not in seen_lines:
                seen_lines.add(normalized)
                combined_lines.append(line_clean)

    # Luego agregar líneas nuevas de otros resultados
    for text in all_texts:
        for line in text.split("\n"):
            line_clean = line.strip()
            if line_clean and len(line_clean) >= 3:
                normalized = "".join(c for c in line_clean.lower() if c.isalnum())
                if normalized and normalized not in seen_lines:
                    # Verificar que no sea solo ruido (al menos 30% alfanumérico)
                    alnum_count = sum(1 for c in line_clean if c.isalnum())
                    if alnum_count / len(line_clean) >= 0.3:
                        seen_lines.add(normalized)
                        combined_lines.append(line_clean)

    combined = "\n".join(combined_lines)
    logger.info(
        f"OCR multi-pass: {len(all_texts)} resultados combinados, "
        f"{len(combined)} chars de {os.path.basename(file_path)}"
    )
    return combined


def extract_text(file_path: str) -> str:
    """Extrae el texto de un archivo. Usa pytesseract directo para imágenes, Tika para el resto."""
    headers = {"Accept": "text/plain"}

    ext = os.path.splitext(file_path)[1].lower()

    # Para imágenes: pipeline OCR directo optimizado (bypass Tika)
    if ext in [".jpg", ".jpeg", ".png"]:
        try:
            return _extract_text_image_direct(file_path)
        except Exception as e:
            logger.warning(f"OCR directo falló para {file_path}: {e}. Cayendo a Tika.")
            # Fallback a Tika si pytesseract falla
            headers["X-Tika-OCRLanguage"] = "spa"
            headers["X-Tika-OCREnableImagePreprocessing"] = "true"
            headers["X-Tika-OCRPageSegMode"] = "11"

    elif ext == ".pdf":
        headers["X-Tika-PDFOcrStrategy"] = "auto"
        headers["X-Tika-OCRLanguage"] = "spa"
        headers["X-Tika-PDFExtractInlineImages"] = "true"
    elif ext in [".txt", ".csv"]:
        headers["Content-Type"] = "text/plain; charset=utf-8"

    try:
        with open(file_path, "rb") as f:
            res_tika = requests.put(settings.TIKA_URL, data=f, headers=headers, timeout=180)
            if res_tika.status_code == 200:
                return res_tika.content.decode("utf-8", errors="ignore")
            else:
                raise Exception(f"Tika retornó status code {res_tika.status_code}")
    except Exception as e:
        raise Exception(f"Error en Apache Tika: {str(e)}")


def check_health() -> bool:
    """Ping a Apache Tika para verificar su salud."""
    try:
        base_url = "/".join(settings.TIKA_URL.split("/")[:3])
        res = requests.get(base_url, timeout=5)
        return res.status_code < 500
    except Exception:
        return False
