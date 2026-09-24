"""Guarded glossary conversion; preserve all historical terminology rows.

Revision ID: 20260916_glossary_single_source
Revises: 20260916_character_voice_timeline
"""
from pathlib import Path
import hashlib
from typing import Sequence, Union

from alembic import op
from alembic.util import load_python_file
import sqlalchemy as sa


revision: str = "20260916_glossary_single_source"
down_revision: Union[str, Sequence[str], None] = "20260916_character_voice_timeline"
branch_labels = None
depends_on = None


def _helper(filename):
    return load_python_file(str(Path(__file__).resolve().parents[1]), filename)


def _key(audit, value):
    return hashlib.sha256(audit.normalized(value).encode('utf-8')).hexdigest()


def _preflight_writers(bind):
    if bind.dialect.name != 'sqlite':
        return
    if bind.execute(sa.text(
        "SELECT 1 FROM sqlite_master WHERE name = '_alembic_tmp_project_glossaries' COLLATE NOCASE "
        "UNION ALL SELECT 1 FROM sqlite_temp_master "
        "WHERE name = '_alembic_tmp_project_glossaries' COLLATE NOCASE")).first():
        raise RuntimeError('Historical schema mismatch: reconcile glossary temporary objects from a backup.')
    for catalog in ('sqlite_master', 'sqlite_temp_master'):
        table_names = bind.execute(sa.text(
            f"SELECT name FROM {catalog} WHERE type = 'table'")).scalars()
        for table_name in table_names:
            if table_name.lower() == 'project_glossaries':
                continue
            foreign_keys = bind.execute(sa.text('SELECT "table" FROM pragma_foreign_key_list(:name)'),
                                        {'name': table_name}).scalars()
            if any(referred.lower() == 'project_glossaries' for referred in foreign_keys):
                raise RuntimeError('Historical schema mismatch: reconcile glossary references from a backup.')
    for table in ('project_glossaries', 'project_terminology_memory'):
        if bind.execute(sa.text(
            "SELECT 1 FROM sqlite_master WHERE type = 'trigger' AND tbl_name = :table COLLATE NOCASE "
            "UNION ALL SELECT 1 FROM sqlite_temp_master WHERE type = 'trigger' "
            "AND tbl_name = :table COLLATE NOCASE"), {'table': table}).first():
            raise RuntimeError('Historical schema mismatch: reconcile glossary triggers from a backup.')
    for name in ('uq_project_glossary_source_key', 'uq_project_glossary_translation_key'):
        if bind.execute(sa.text(
            'SELECT 1 FROM sqlite_master WHERE name = :name COLLATE NOCASE '
            'UNION ALL SELECT 1 FROM sqlite_temp_master WHERE name = :name COLLATE NOCASE'),
            {'name': name}).first():
            raise RuntimeError('Historical schema mismatch: reconcile glossary index names from a backup.')


def _read_rows(bind):
    glossary = [dict(table='project_glossaries', id=row.id, project_id=row.project_id,
                     source_term=row.source_term, translated_term=row.translated_term)
                for row in bind.execute(sa.text(
                    'SELECT id, project_id, source_term, translated_term FROM project_glossaries'))]
    memory = [dict(table='project_terminology_memory', id=row.id, project_id=row.project_id,
                   source_term=row.source_term, translated_term=row.suggested_term)
              for row in bind.execute(sa.text(
                  'SELECT id, project_id, source_term, suggested_term FROM project_terminology_memory'))]
    return glossary, memory


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'mysql':
        raise RuntimeError('Historical schema mismatch: MySQL glossary collation preflight '
                           'is required before conversion; reconcile from a verified backup.')
    helper = _helper('glossary_prerequisites.py')
    audit_helper = _helper('glossary_data_audit.py')
    if 'project_glossaries' in sa.inspect(bind).get_table_names():
        columns = {column['name'] for column in sa.inspect(bind).get_columns('project_glossaries')}
        keys = {'source_key', 'translation_key'} & columns
        if keys:
            if len(keys) != 2:
                helper._mismatch()
            helper.validate_converted(bind)
            glossary, _ = _read_rows(bind)
            for row in glossary:
                stored = bind.execute(sa.text(
                    'SELECT source_key, translation_key FROM project_glossaries WHERE id=:id'),
                    {'id': row['id']}).one()
                if (stored.source_key != _key(audit_helper, row['source_term'])
                        or stored.translation_key != _key(audit_helper, row['translated_term'])):
                    helper._mismatch()
            return
    _preflight_writers(bind)
    helper.ensure(bind)
    glossary, memory = _read_rows(bind)
    result = audit_helper.audit(glossary + memory)
    if result.conflict_codes:
        raise RuntimeError('GLOSSARY_MIGRATION_CONFLICT: ' + ', '.join(result.conflict_codes)
                           + '; reconcile from a verified backup before retrying.')

    op.add_column('project_glossaries', sa.Column('source_key', sa.String(64), nullable=True))
    op.add_column('project_glossaries', sa.Column('translation_key', sa.String(64), nullable=True))
    for row in glossary:
        bind.execute(sa.text(
            'UPDATE project_glossaries SET source_key=:source_key, '
            'translation_key=:translation_key WHERE id=:id'),
            {'id': row['id'], 'source_key': _key(audit_helper, row['source_term']),
             'translation_key': _key(audit_helper, row['translated_term'])})

    memory_by_id = {str(row['id']): row for row in memory}
    for identity in result.import_ids:
        row = memory_by_id[identity]
        bind.execute(sa.text(
            'INSERT INTO project_glossaries '
            '(id, project_id, source_term, translated_term, term_type, confidence, '
            'source_context, approved, created_at, updated_at, source_key, translation_key) '
            'SELECT id, project_id, source_term, suggested_term, term_type, confidence, '
            'source_context, CASE WHEN needs_review = 0 THEN 1 ELSE 0 END, '
            'created_at, updated_at, :source_key, :translation_key '
            'FROM project_terminology_memory WHERE id=:id'),
            {'id': identity, 'source_key': _key(audit_helper, row['source_term']),
             'translation_key': _key(audit_helper, row['translated_term'])})

    with op.batch_alter_table('project_glossaries') as batch:
        batch.alter_column('source_key', existing_type=sa.String(64), nullable=False)
        batch.alter_column('translation_key', existing_type=sa.String(64), nullable=False)
        batch.create_unique_constraint('uq_project_glossary_source_key', ['project_id', 'source_key'])
        batch.create_unique_constraint('uq_project_glossary_translation_key',
                                       ['project_id', 'translation_key'])


def downgrade() -> None:
    raise RuntimeError('Cannot safely downgrade the glossary conversion; '
                       'restore a verified backup instead.')
