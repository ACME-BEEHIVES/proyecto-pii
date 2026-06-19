import os
import time
import json
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.database import SessionLocal
from app.models.scan_config import ScanConfig
from app.services.path_service import translate_path
from app.services import scan_engine

class PiiFileHandler(FileSystemEventHandler):
    def __init__(self, extensions: list[str], entities: list[str]):
        self.extensions = extensions
        self.entities = entities

    def on_modified(self, event):
        if not event.is_directory:
            self.process(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.process(event.src_path)

    def process(self, file_path: str):
        # Evitar escanear archivos temporales, censurados o de cuarentena
        path_lower = file_path.lower()
        if "quarantine" in path_lower or "censurado" in path_lower or "redacted" in path_lower or file_path.endswith(".quarantine.txt"):
            return
            
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.extensions:
            return

        # Pequeño sleep para dar tiempo a que se libere el archivo después de escribirlo
        time.sleep(0.5)
        
        # Procesar en un hilo separado
        thread = threading.Thread(
            target=self._scan_file,
            args=(file_path,),
            daemon=True
        )
        thread.start()

    def _scan_file(self, file_path: str):
        # Normalizar barras para que coincida con las almacenadas
        normalized_path = file_path.replace('\\', '/')
        try:
            print(f"[Watcher] Escaneando archivo modificado: {normalized_path}")
            scan_engine.process_file(normalized_path, None, self.entities)
        except Exception as e:
            print(f"[Watcher] Error procesando archivo {normalized_path}: {e}")


class RealtimeWatcher:
    def __init__(self):
        self.observer = None
        self.current_paths = set()
        self.active = True
        self.lock = threading.Lock()

    def start(self):
        print("[Watcher] Iniciando servicio de monitoreo en tiempo real...")
        thread = threading.Thread(target=self._run_loop, daemon=True)
        thread.start()

    def _run_loop(self):
        while self.active:
            try:
                db = SessionLocal()
                config = db.query(ScanConfig).first()
                if not config or not config.is_active:
                    db.close()
                    time.sleep(10)
                    continue

                # Cargar configuraciones
                try:
                    paths = set(json.loads(config.scan_paths))
                    extensions = json.loads(config.extensions)
                    entities = json.loads(config.entities)
                except Exception:
                    db.close()
                    time.sleep(10)
                    continue

                db.close()

                # Traducir a rutas locales
                translated_paths = set()
                for p in paths:
                    tp = translate_path(p)
                    if os.path.exists(tp):
                        translated_paths.add(tp)

                # Si cambiaron las rutas, reiniciar el observador
                if translated_paths != self.current_paths:
                    with self.lock:
                        print(f"[Watcher] Detectado cambio en rutas monitoreadas. Reiniciando observador...")
                        self._stop_observer()
                        self.current_paths = translated_paths
                        self._start_observer(translated_paths, extensions, entities)

            except Exception as e:
                print(f"[Watcher] Error en bucle del observador: {e}")

            time.sleep(10)

    def _start_observer(self, paths: set[str], extensions: list[str], entities: list[str]):
        if not paths:
            return
        self.observer = Observer()
        handler = PiiFileHandler(extensions, entities)
        for p in paths:
            try:
                self.observer.schedule(handler, path=p, recursive=True)
                print(f"[Watcher] Monitoreando carpeta: {p}")
            except Exception as e:
                print(f"[Watcher] No se pudo iniciar monitoreo en {p}: {e}")
        try:
            self.observer.start()
        except Exception as e:
            print(f"[Watcher] Error al iniciar observador de eventos: {e}")

    def _stop_observer(self):
        if self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=2)
            except Exception:
                pass
            self.observer = None

    def stop(self):
        self.active = False
        self._stop_observer()

watcher = RealtimeWatcher()
