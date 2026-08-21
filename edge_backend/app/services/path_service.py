import os

# Mapeo de prefijos de ruta del host (Windows) a rutas dentro del contenedor Docker.
# Debe reflejar los volumes definidos en docker-compose.yml. A diferencia de la
# version anterior, esto NO depende de un nombre de usuario especifico: cubre a
# cualquier usuario de Windows que tenga su carpeta bajo C:\Users (Carlos, Pablo,
# o quien instale esto en un cliente), sin hardcodear una persona puntual.
#
# Para escanear otra unidad (D:\, un recurso de red, etc.) agregar el mount
# correspondiente en docker-compose.yml (ej. "- D:\:/mnt/d:ro") y una entrada
# aqui (ej. (r"D:", "/mnt/d")).
MOUNT_MAP: list[tuple[str, str]] = [
    (r"C:\Users", "/mnt/c/Users"),
]


def translate_path(path: str) -> str:
    """Traduce una ruta de Windows del host a la ruta equivalente dentro del
    contenedor Docker, segun los volumes definidos en docker-compose.yml.

    Las rutas que ya corresponden a una carpeta del proyecto montada de forma
    relativa (./CARPETA_PRUEBA_MASIVA:/app/CARPETA_PRUEBA_MASIVA, etc.) se
    ingresan directamente en su forma de contenedor (ej. "/app/RRHH") y pasan
    sin traduccion.

    Si la ruta no cae bajo ningun mount conocido, se devuelve tal cual (y el
    caller determinara que no existe / no es accesible).
    """
    p = path.strip().strip('"').strip("'").strip()
    if not p:
        return p

    if not os.path.exists("/.dockerenv"):
        return p

    normalized = p.replace("/", "\\")
    normalized_lower = normalized.lower()

    for prefix, target_dir in MOUNT_MAP:
        if normalized_lower.startswith(prefix.lower()):
            relative = normalized[len(prefix):].lstrip("\\").lstrip("/")
            translated = os.path.join(target_dir, relative)
            return translated.replace("\\", "/")

    return p
