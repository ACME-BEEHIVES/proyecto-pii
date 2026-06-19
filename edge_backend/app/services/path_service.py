import os

def translate_path(path: str) -> str:
    """Traduce rutas de Windows del host a rutas del contenedor Docker (/app)
    si pertenecen al directorio del proyecto montado.
    """
    p = path.strip().strip('"').strip("'").strip()
    if not p:
        return p
        
    # Si no estamos corriendo dentro de un contenedor Docker, no traducir la ruta
    if not os.path.exists("/.dockerenv"):
        return p
        
    # Normalizar barras a diagonal invertida para facilitar el matching de prefijos Windows
    normalized = p.replace('/', '\\')
    
    # Mapeos de prefijos del host a rutas del contenedor
    translation_mappings = [
        (r"c:\users\pabloortizcollados\desktop\proyecto-pii", "/app"),
        (r"users\pabloortizcollados\desktop\proyecto-pii", "/app"),
        (r"c:\users\pabloortizcollados\desktop\archivos prueba pii", "/Archivos_Prueba_PII"),
        (r"users\pabloortizcollados\desktop\archivos prueba pii", "/Archivos_Prueba_PII")
    ]
    
    for prefix, target_dir in translation_mappings:
        if normalized.lower().startswith(prefix):
            # Extraer la parte relativa después del prefijo
            relative = normalized[len(prefix):]
            # Quitar barras sobrantes al inicio de la ruta relativa
            relative = relative.lstrip('\\').lstrip('/')
            # Unir con la ruta destino en el contenedor
            translated = os.path.join(target_dir, relative)
            # Retornar con barras normales compatibles con Linux/Docker
            return translated.replace('\\', '/')
            
    return p
