import os
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
from app.services import crypto_service
from app.models.finding import ScanFinding
from sqlalchemy.orm import Session
import shutil

def get_texts_to_redact(file_path: str, db: Session) -> list[str]:
    """Obtiene y descifra todos los textos de hallazgos asociados a un archivo."""
    findings = db.query(ScanFinding).filter(
        ScanFinding.file_path == file_path
    ).all()
    
    texts = []
    for f in findings:
        if f.is_sensitive and f.detected_text:
            decrypted = crypto_service.decrypt(f.detected_text)
            if decrypted and decrypted not in texts:
                texts.append(decrypted)
        elif f.detected_text:
            if f.detected_text not in texts:
                texts.append(f.detected_text)
    return texts

def redact_pdf(input_path: str, output_path: str, texts: list[str]):
    """Censura texto sensible en un PDF dibujando rectángulos negros."""
    doc = fitz.open(input_path)
    for page in doc:
        for text in texts:
            if not text or len(text.strip()) < 2:
                continue
            rects = page.search_for(text)
            for rect in rects:
                # Añadir anotación de censura (caja negra)
                page.add_redact_annot(rect, fill=(0, 0, 0))
        page.apply_redact_annots()
    doc.save(output_path)
    doc.close()

def redact_text_file(input_path: str, output_path: str, texts: list[str]):
    """Reemplaza texto sensible en archivos plano con la etiqueta [REDACTADO]."""
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    for text in texts:
        if not text or len(text.strip()) < 2:
            continue
        content = content.replace(text, "[REDACTADO]")
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

def _normalize_for_match(text: str) -> str:
    """Normaliza texto para comparación flexible (sin puntos, guiones, espacios, minúsculas)."""
    import re as _re
    return _re.sub(r'[^a-záéíóúñü0-9]', '', text.lower().strip())

def redact_image(input_path: str, output_path: str, texts: list[str]):
    """Dibuja cajas negras sobre las ubicaciones reales del texto PII en la imagen usando OCR."""
    import pytesseract

    img = Image.open(input_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    # Obtener datos OCR con bounding boxes a nivel de palabra
    ocr_data = pytesseract.image_to_data(img, lang='spa', output_type=pytesseract.Output.DICT)
    
    n_boxes = len(ocr_data['text'])
    
    # Normalizar los textos PII a buscar
    normalized_texts = []
    for t in texts:
        if t and len(t.strip()) >= 2:
            normalized_texts.append((t, _normalize_for_match(t)))
    
    if not normalized_texts:
        img.save(output_path)
        return
    
    # Para cada texto PII, buscar coincidencias en las palabras OCR
    # Construir lista de palabras OCR con sus posiciones
    ocr_words = []
    for i in range(n_boxes):
        word = ocr_data['text'][i].strip()
        conf = int(ocr_data['conf'][i])
        if word and conf > 0:  # Solo palabras con confianza > 0
            ocr_words.append({
                'text': word,
                'normalized': _normalize_for_match(word),
                'left': ocr_data['left'][i],
                'top': ocr_data['top'][i],
                'width': ocr_data['width'][i],
                'height': ocr_data['height'][i],
                'index': i
            })
    
    # Marcar las palabras que coinciden con algún texto PII
    boxes_to_draw = []
    
    for pii_text, pii_norm in normalized_texts:
        pii_words = pii_norm.split() if ' ' in pii_text else []
        
        for ow in ocr_words:
            matched = False
            
            # Match 1: La palabra OCR normalizada está contenida en el PII normalizado
            if len(ow['normalized']) >= 2 and ow['normalized'] in pii_norm:
                matched = True
            
            # Match 2: El PII normalizado está contenido en la palabra OCR
            if len(pii_norm) >= 3 and pii_norm in ow['normalized']:
                matched = True
            
            # Match 3: Match exacto de palabra normalizada
            if ow['normalized'] == pii_norm:
                matched = True
                
            # Match 4: Para RUTs y números, comparar solo dígitos
            if not matched and any(c.isdigit() for c in pii_norm):
                import re as _re
                pii_digits = _re.sub(r'[^0-9]', '', pii_text)
                ocr_digits = _re.sub(r'[^0-9]', '', ow['text'])
                if len(pii_digits) >= 5 and len(ocr_digits) >= 5:
                    if pii_digits in ocr_digits or ocr_digits in pii_digits:
                        matched = True
            
            if matched:
                padding = 4  # Pequeño padding para cubrir mejor
                boxes_to_draw.append((
                    ow['left'] - padding,
                    ow['top'] - padding,
                    ow['left'] + ow['width'] + padding,
                    ow['top'] + ow['height'] + padding
                ))
    
    # Dibujar las cajas negras sobre las coincidencias
    for box in boxes_to_draw:
        draw.rectangle(box, fill="black")
    
    img.save(output_path)

def redact_file(file_path: str, db: Session, output_dir: str) -> str:
    """Función principal para censurar un archivo según su tipo."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
    texts = get_texts_to_redact(file_path, db)
    if not texts:
        # Si no hay hallazgos PII, simplemente devolvemos una copia del original
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, os.path.basename(file_path))
        shutil.copy(file_path, output_path)
        return output_path
        
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(file_path)
    base, ext = os.path.splitext(filename)
    redacted_filename = f"{base}_censurado{ext}"
    output_path = os.path.join(output_dir, redacted_filename)
    
    ext_lower = ext.lower()
    if ext_lower == ".pdf":
        redact_pdf(file_path, output_path, texts)
    elif ext_lower in [".txt", ".csv"]:
        redact_text_file(file_path, output_path, texts)
    elif ext_lower in [".jpg", ".jpeg", ".png"]:
        redact_image(file_path, output_path, texts)
    else:
        # Fallback de copiado si la extensión es compleja (Word, Excel)
        shutil.copy(file_path, output_path)
        
    return output_path

def redact_file_in_place(file_path: str, db: Session) -> bool:
    """Censura y sobreescribe directamente el archivo original."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    
    # 1. Crear el archivo censurado en una carpeta temporal (/tmp)
    temp_dir = "/tmp/redaction"
    os.makedirs(temp_dir, exist_ok=True)
    temp_output_path = redact_file(file_path, db, temp_dir)
    
    # 2. Copiar el archivo temporal sobre el original
    shutil.copy(temp_output_path, file_path)
    
    # 3. Eliminar el archivo temporal
    if os.path.exists(temp_output_path):
        os.remove(temp_output_path)
        
    # 4. Marcar todos los hallazgos del archivo como resueltos
    from datetime import datetime
    findings = db.query(ScanFinding).filter(
        ScanFinding.file_path == file_path
    ).all()
    for f in findings:
        f.is_resolved = True
        f.resolved_at = datetime.utcnow()
        f.resolved_by = "Sistema"
        f.resolution_method = "redacted_in_place"
        f.resolution_notes = "Archivo censurado y sobreescrito en origen automáticamente."
    db.commit()
    return True

def quarantine_file(file_path: str, db: Session) -> str:
    """Mueve el archivo original a la carpeta de cuarentena, deja un placeholder y actualiza la BD."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
    # 1. Definir carpeta de cuarentena dentro del contenedor (/app/quarantine)
    app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    quarantine_dir = os.path.join(app_dir, "quarantine")
    os.makedirs(quarantine_dir, exist_ok=True)
    
    # 2. Mover el archivo a la cuarentena
    filename = os.path.basename(file_path)
    dest_path = os.path.join(quarantine_dir, filename)
    
    # Manejar colisiones de nombres en cuarentena
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(quarantine_dir, f"{base}_{counter}{ext}")
        counter += 1
        
    shutil.move(file_path, dest_path)
    
    # 3. Crear archivo placeholder en el lugar original indicando que fue puesto en cuarentena
    placeholder_text = (
        f"Este archivo ({filename}) fue puesto en cuarentena por contener "
        f"datos personales sensibles bajo la Ley 21.719.\n"
        f"Ubicación en cuarentena: {os.path.basename(dest_path)}\n"
    )
    placeholder_path = file_path + ".quarantine.txt"
    with open(placeholder_path, 'w', encoding='utf-8') as f:
        f.write(placeholder_text)
        
    # 4. Actualizar todos los hallazgos en la BD
    from datetime import datetime
    from app.models.file_control import FileControl
    
    # Buscar todos los hallazgos asociados a la ruta original
    findings = db.query(ScanFinding).filter(
        ScanFinding.file_path == file_path
    ).all()
    
    # Actualizar la ruta del archivo y marcarlos como resueltos
    for f in findings:
        f.file_path = dest_path
        f.file_name = os.path.basename(dest_path)
        f.is_resolved = True
        f.resolved_at = datetime.utcnow()
        f.resolved_by = "Sistema"
        f.resolution_method = "quarantined"
        f.resolution_notes = f"Archivo movido a cuarentena: {os.path.basename(dest_path)}"
        
    # También actualizar el control de archivos si existe
    file_ctrl = db.query(FileControl).filter(
        FileControl.file_path == file_path
    ).first()
    if file_ctrl:
        file_ctrl.file_path = dest_path
        file_ctrl.file_name = os.path.basename(dest_path)
        
    db.commit()
    return dest_path
