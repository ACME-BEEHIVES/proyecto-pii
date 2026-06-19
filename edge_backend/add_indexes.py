from sqlalchemy import text
from app.database import SessionLocal

db = SessionLocal()

# Agregar indice en archivo_nombre (file_path) - prefix index para TEXT columns
db.execute(text('CREATE INDEX idx_control_archivos_file_path ON control_archivos (archivo_nombre(255))'))
db.commit()
print('Indice idx_control_archivos_file_path creado OK')

# Agregar indice en hash_archivo (content_hash) para lookups rapidos
db.execute(text('CREATE INDEX idx_control_archivos_content_hash ON control_archivos (hash_archivo)'))
db.commit()
print('Indice idx_control_archivos_content_hash creado OK')

# Verificar
result = db.execute(text('SHOW INDEX FROM control_archivos'))
for row in result:
    m = dict(row._mapping)
    print(f"  {m['Key_name']:45s} -> {m['Column_name']:20s} ({m['Index_type']})")

# Tambien agregar indices a la tabla hallazgos
print('\n--- Indices tabla hallazgos ---')
try:
    db.execute(text('CREATE INDEX idx_hallazgos_tipo_entidad ON hallazgos (tipo_entidad)'))
    db.commit()
    print('Indice idx_hallazgos_tipo_entidad creado OK')
except Exception as e:
    print(f'idx_hallazgos_tipo_entidad ya existe o error: {e}')
    db.rollback()

try:
    db.execute(text('CREATE INDEX idx_hallazgos_archivo ON hallazgos (archivo_nombre(255))'))
    db.commit()
    print('Indice idx_hallazgos_archivo creado OK')
except Exception as e:
    print(f'idx_hallazgos_archivo ya existe o error: {e}')
    db.rollback()

try:
    db.execute(text('CREATE INDEX idx_hallazgos_is_resolved ON hallazgos (is_resolved)'))
    db.commit()
    print('Indice idx_hallazgos_is_resolved creado OK')
except Exception as e:
    print(f'idx_hallazgos_is_resolved ya existe o error: {e}')
    db.rollback()

try:
    db.execute(text('CREATE INDEX idx_hallazgos_is_sensitive ON hallazgos (is_sensitive)'))
    db.commit()
    print('Indice idx_hallazgos_is_sensitive creado OK')
except Exception as e:
    print(f'idx_hallazgos_is_sensitive ya existe o error: {e}')
    db.rollback()

try:
    db.execute(text('CREATE INDEX idx_hallazgos_scan_job ON hallazgos (scan_job_id)'))
    db.commit()
    print('Indice idx_hallazgos_scan_job creado OK')
except Exception as e:
    print(f'idx_hallazgos_scan_job ya existe o error: {e}')
    db.rollback()

# Mostrar todos los indices de hallazgos
result2 = db.execute(text('SHOW INDEX FROM hallazgos'))
for row in result2:
    m = dict(row._mapping)
    print(f"  {m['Key_name']:45s} -> {m['Column_name']:20s} ({m['Index_type']})")

db.close()
print('\nDone!')
