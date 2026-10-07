"""initial_sqlite

Revision ID: eec59b6a5a86
Revises: 
Create Date: 2026-07-30 11:12:46.227479

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eec59b6a5a86'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'control_archivos' not in existing_tables:
        op.create_table('control_archivos',
        sa.Column('hash_ruta', sa.String(length=64), nullable=False),
        sa.Column('archivo_nombre', sa.String(length=750), nullable=True),
        sa.Column('hash_archivo', sa.String(length=64), nullable=True),
        sa.Column('ultima_actualizacion', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('hash_ruta', name=op.f('pk_control_archivos'))
        )
        with op.batch_alter_table('control_archivos', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_control_archivos_archivo_nombre'), ['archivo_nombre'], unique=False)
            batch_op.create_index(batch_op.f('ix_control_archivos_hash_archivo'), ['hash_archivo'], unique=False)

    if 'db_configs' not in existing_tables:
        op.create_table('db_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=191), nullable=False),
        sa.Column('db_type', sa.String(length=50), nullable=False),
        sa.Column('connection_string', sa.Text(), nullable=False),
        sa.Column('tables_to_scan', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_db_configs')),
        sa.UniqueConstraint('name', name=op.f('uq_db_configs_name'))
        )

    if 'scan_configs' not in existing_tables:
        op.create_table('scan_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('scan_paths', sa.Text(), nullable=False),
        sa.Column('extensions', sa.Text(), nullable=False),
        sa.Column('entities', sa.Text(), nullable=False),
        sa.Column('max_workers', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('schedule_type', sa.String(length=50), server_default='none', nullable=False),
        sa.Column('schedule_time', sa.String(length=10), server_default='00:00', nullable=False),
        sa.Column('schedule_day', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_scheduled_run', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_scan_configs'))
        )

    if 'scan_jobs' not in existing_tables:
        op.create_table('scan_jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('root_path', sa.String(length=1024), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('files_total', sa.Integer(), nullable=False),
        sa.Column('files_scanned', sa.Integer(), nullable=False),
        sa.Column('files_skipped', sa.Integer(), nullable=False),
        sa.Column('findings_count', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_scan_jobs'))
        )

    if 'hallazgos' not in existing_tables:
        op.create_table('hallazgos',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('scan_job_id', sa.Integer(), nullable=True),
        sa.Column('archivo_nombre', sa.String(length=750), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('tipo_entidad', sa.String(length=50), nullable=True),
        sa.Column('texto_detectado', sa.Text(), nullable=True),
        sa.Column('search_hash', sa.String(length=64), nullable=True),
        sa.Column('puntaje_certeza', sa.Float(), nullable=True),
        sa.Column('is_sensitive', sa.Boolean(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.String(length=100), nullable=True),
        sa.Column('resolution_method', sa.String(length=50), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('fecha_deteccion', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['scan_job_id'], ['scan_jobs.id'], name=op.f('fk_hallazgos_scan_job_id_scan_jobs')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_hallazgos'))
        )
        with op.batch_alter_table('hallazgos', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_hallazgos_archivo_nombre'), ['archivo_nombre'], unique=False)
            batch_op.create_index(batch_op.f('ix_hallazgos_is_resolved'), ['is_resolved'], unique=False)
            batch_op.create_index(batch_op.f('ix_hallazgos_is_sensitive'), ['is_sensitive'], unique=False)
            batch_op.create_index(batch_op.f('ix_hallazgos_scan_job_id'), ['scan_job_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_hallazgos_search_hash'), ['search_hash'], unique=False)
            batch_op.create_index(batch_op.f('ix_hallazgos_tipo_entidad'), ['tipo_entidad'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('hallazgos', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_hallazgos_tipo_entidad'))
        batch_op.drop_index(batch_op.f('ix_hallazgos_search_hash'))
        batch_op.drop_index(batch_op.f('ix_hallazgos_scan_job_id'))
        batch_op.drop_index(batch_op.f('ix_hallazgos_is_sensitive'))
        batch_op.drop_index(batch_op.f('ix_hallazgos_is_resolved'))
        batch_op.drop_index(batch_op.f('ix_hallazgos_archivo_nombre'))

    op.drop_table('hallazgos')
    op.drop_table('scan_jobs')
    op.drop_table('scan_configs')
    op.drop_table('db_configs')

    with op.batch_alter_table('control_archivos', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_control_archivos_hash_archivo'))
        batch_op.drop_index(batch_op.f('ix_control_archivos_archivo_nombre'))

    op.drop_table('control_archivos')
