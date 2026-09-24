"""Guarded glossary conversion; preserve all historical terminology rows.

Revision ID: 20260916_glossary_single_source
Revises: 20260916_character_voice_timeline
"""
from pathlib import Path
import hashlib
import json
from typing import Sequence, Union

from alembic import op
from alembic.util import load_python_file
import sqlalchemy as sa


revision: str = "20260916_glossary_single_source"
down_revision: Union[str, Sequence[str], None] = "20260916_character_voice_timeline"
branch_labels = None
depends_on = None

_MYSQL_STAGE = '__alembic_glossary_stage_20260916'
_MYSQL_BACKUP = '__alembic_glossary_before_20260916'
_MYSQL_AUDIT = '__alembic_glossary_audit_20260916'


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
    glossary = [dict(table='project_glossaries', **row)
                for row in bind.execute(sa.text('SELECT * FROM project_glossaries')).mappings()]
    memory = [dict(table='project_terminology_memory',
                   **{**row, 'translated_term': row['suggested_term']})
              for row in bind.execute(sa.text(
                  'SELECT * FROM project_terminology_memory')).mappings()]
    return glossary, memory


def _mysql_preflight_objects(bind, names, allow_stage=False):
    inspector = sa.inspect(bind)
    occupied = {name.lower() for name in inspector.get_table_names() + inspector.get_view_names()}
    if ((_MYSQL_STAGE.lower() in occupied and not allow_stage)
            or (allow_stage and _MYSQL_STAGE not in names)
            or _MYSQL_BACKUP.lower() in occupied
            or (_MYSQL_AUDIT.lower() in occupied and not allow_stage)
            or (allow_stage and _MYSQL_AUDIT not in names)):
        raise RuntimeError('Historical schema mismatch: reconcile glossary stage and backup names '
                           'from a verified backup before retrying.')
    if bind.execute(sa.text(
        "SELECT 1 FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA = DATABASE() "
        "AND EVENT_OBJECT_TABLE IN ('project_glossaries', 'project_terminology_memory') "
        "LIMIT 1")).first():
        raise RuntimeError('Historical schema mismatch: reconcile glossary triggers from a backup.')
    if bind.execute(sa.text(
        "SELECT 1 FROM information_schema.KEY_COLUMN_USAGE "
        "WHERE REFERENCED_TABLE_SCHEMA = DATABASE() "
        "AND REFERENCED_TABLE_NAME = 'project_glossaries' "
        "AND TABLE_NAME <> 'project_glossaries' LIMIT 1")).first():
        raise RuntimeError('Historical schema mismatch: reconcile glossary references from a backup.')


def _mysql_expected_alias(helper, name):
    _, (glossary, _) = helper._tables()
    alias = glossary.to_metadata(glossary.metadata, name=name)
    for index in alias.indexes:
        if index.columns.keys() == ['project_id']:
            index.name = 'ix_project_glossaries_project_id'
    return alias


def _mysql_expected_stage(helper):
    stage = _mysql_expected_alias(helper, _MYSQL_STAGE)
    stage.append_column(sa.Column('source_key', sa.String(64), nullable=False))
    stage.append_column(sa.Column('translation_key', sa.String(64), nullable=False))
    stage.append_constraint(sa.UniqueConstraint(
        'project_id', 'source_key', name='uq_project_glossary_source_key'))
    stage.append_constraint(sa.UniqueConstraint(
        'project_id', 'translation_key', name='uq_project_glossary_translation_key'))
    return stage


def _mysql_build_stage(bind):
    bind.exec_driver_sql(f'CREATE TABLE `{_MYSQL_STAGE}` LIKE `project_glossaries`')
    bind.exec_driver_sql(
        f'ALTER TABLE `{_MYSQL_STAGE}` '
        'ADD COLUMN `source_key` VARCHAR(64) NOT NULL, '
        'ADD COLUMN `translation_key` VARCHAR(64) NOT NULL, '
        'ADD CONSTRAINT `uq_project_glossary_source_key` UNIQUE (`project_id`, `source_key`), '
        'ADD CONSTRAINT `uq_project_glossary_translation_key` UNIQUE (`project_id`, `translation_key`), '
        'ADD FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE')


def _mysql_build_audit(bind):
    bind.exec_driver_sql(
        f'CREATE TABLE `{_MYSQL_AUDIT}` ('
        '`id` TINYINT NOT NULL PRIMARY KEY, '
        '`row_count` BIGINT UNSIGNED NOT NULL, '
        '`sha256` BINARY(32) NOT NULL)')


def _mysql_backup_fingerprint(rows):
    payload = [{key: value for key, value in row.items() if key != 'table'}
               for row in sorted(rows, key=lambda row: str(row['id']))]
    encoded = json.dumps(payload, default=str, sort_keys=True, ensure_ascii=False,
                         separators=(',', ':')).encode('utf-8')
    return len(rows), hashlib.sha256(encoded).digest()


def _mysql_validate_audit(bind, helper, expected=None):
    inspector = sa.inspect(bind)
    if _MYSQL_AUDIT not in inspector.get_table_names():
        helper._mismatch()
    columns = {column['name']: column for column in inspector.get_columns(_MYSQL_AUDIT)}
    kinds = {name: column['type'].compile(dialect=bind.dialect) for name, column in columns.items()}
    if (kinds != {'id': 'TINYINT', 'row_count': 'BIGINT UNSIGNED', 'sha256': 'BINARY(32)'}
            or any(column['nullable'] or column.get('default') is not None
                   for column in columns.values())
            or inspector.get_pk_constraint(_MYSQL_AUDIT)['constrained_columns'] != ['id']
            or inspector.get_foreign_keys(_MYSQL_AUDIT)
            or inspector.get_unique_constraints(_MYSQL_AUDIT)
            or inspector.get_check_constraints(_MYSQL_AUDIT)
            or inspector.get_indexes(_MYSQL_AUDIT)):
        helper._mismatch()
    rows = bind.exec_driver_sql(f'SELECT id, row_count, sha256 FROM `{_MYSQL_AUDIT}`').all()
    if len(rows) != 1 or rows[0].id != 1 or rows[0].row_count < 0 or len(rows[0].sha256) != 32:
        helper._mismatch()
    if expected is not None and (rows[0].row_count, rows[0].sha256) != expected:
        helper._mismatch()
    return rows[0].row_count, rows[0].sha256


def _mysql_copy_stage(bind, audit_helper, glossary, memory, result):
    for row in glossary:
        bind.execute(sa.text(
            f'INSERT INTO `{_MYSQL_STAGE}` '
            '(id, project_id, source_term, translated_term, term_type, confidence, '
            'source_context, approved, created_at, updated_at, source_key, translation_key) '
            'SELECT id, project_id, source_term, translated_term, term_type, confidence, '
            'source_context, approved, created_at, updated_at, :source_key, :translation_key '
            'FROM project_glossaries WHERE id=:id'),
            {'id': row['id'], 'source_key': _key(audit_helper, row['source_term']),
             'translation_key': _key(audit_helper, row['translated_term'])})
    memory_by_id = {str(row['id']): row for row in memory}
    for identity in result.import_ids:
        row = memory_by_id[identity]
        bind.execute(sa.text(
            f'INSERT INTO `{_MYSQL_STAGE}` '
            '(id, project_id, source_term, translated_term, term_type, confidence, '
            'source_context, approved, created_at, updated_at, source_key, translation_key) '
            'SELECT id, project_id, source_term, suggested_term, term_type, confidence, '
            'source_context, CASE WHEN needs_review = 0 THEN 1 ELSE 0 END, '
            'created_at, updated_at, :source_key, :translation_key '
            'FROM project_terminology_memory WHERE id=:id'),
            {'id': identity, 'source_key': _key(audit_helper, row['source_term']),
             'translation_key': _key(audit_helper, row['translated_term'])})


def _mysql_verify_stage(bind, helper, audit_helper, glossary, memory, result):
    _mysql_preflight_objects(bind, set(sa.inspect(bind).get_table_names()), allow_stage=True)
    helper._preflight(bind)
    stage = _mysql_expected_stage(helper)
    helper._validate_table(bind, sa.inspect(bind), stage, converted=True)
    current_glossary, current_memory = _read_rows(bind)
    for expected_rows, current_rows in ((glossary, current_glossary), (memory, current_memory)):
        if ({str(row['id']): row for row in expected_rows}
                != {str(row['id']): row for row in current_rows}):
            helper._mismatch()
    source = {str(row['id']): row for row in glossary + memory
              if row['table'] == 'project_glossaries' or str(row['id']) in result.import_ids}
    actual = bind.execute(sa.text(f'SELECT * FROM `{_MYSQL_STAGE}`')).mappings().all()
    if len(actual) != len(source):
        helper._mismatch()
    for row in actual:
        expected = source.get(str(row['id']))
        if expected is None:
            helper._mismatch()
        expected_copy = {name: expected[name] for name in (
            'id', 'project_id', 'source_term', 'translated_term', 'term_type',
            'confidence', 'source_context', 'created_at', 'updated_at')}
        expected_copy['approved'] = (expected['approved'] if expected['table'] ==
                                     'project_glossaries' else int(not expected['needs_review']))
        expected_copy['source_key'] = _key(audit_helper, expected['source_term'])
        expected_copy['translation_key'] = _key(audit_helper, expected['translated_term'])
        if dict(row) != expected_copy:
            helper._mismatch()


def _mysql_upgrade(bind, helper, audit_helper):
    inspector = sa.inspect(bind)
    names = set(inspector.get_table_names())
    occupied = {name.lower() for name in names | set(inspector.get_view_names())}
    if _MYSQL_STAGE.lower() in occupied:
        helper._mismatch()
    if 'project_glossaries' in names:
        columns = {column['name'] for column in inspector.get_columns('project_glossaries')}
        keys = {'source_key', 'translation_key'} & columns
        if keys:
            if len(keys) != 2:
                helper._mismatch()
            if _MYSQL_BACKUP not in names:
                helper._mismatch()
            helper.validate_converted(bind)
            helper._validate_table(bind, inspector,
                                   _mysql_expected_alias(helper, _MYSQL_BACKUP))
            backup = [dict(row) for row in bind.execute(sa.text(
                f'SELECT * FROM `{_MYSQL_BACKUP}`')).mappings()]
            _mysql_validate_audit(bind, helper, _mysql_backup_fingerprint(backup))
            glossary, _ = _read_rows(bind)
            for row in glossary:
                stored = bind.execute(sa.text(
                    'SELECT source_key, translation_key FROM project_glossaries WHERE id=:id'),
                    {'id': row['id']}).one()
                if (stored.source_key != _key(audit_helper, row['source_term'])
                        or stored.translation_key != _key(audit_helper, row['translated_term'])):
                    helper._mismatch()
            return
    _mysql_preflight_objects(bind, names)
    _, present = helper._preflight(bind)
    if present:
        glossary, memory = _read_rows(bind)
        collision_codes = _helper('glossary_mysql_preflight.py').collision_codes(bind)
        if collision_codes:
            raise RuntimeError('GLOSSARY_MIGRATION_CONFLICT: ' + ', '.join(collision_codes)
                               + '; reconcile from a verified backup before retrying.')
        result = audit_helper.audit(glossary + memory)
        if result.conflict_codes:
            raise RuntimeError('GLOSSARY_MIGRATION_CONFLICT: ' + ', '.join(result.conflict_codes)
                               + '; reconcile from a verified backup before retrying.')
    helper.ensure(bind)
    if not present:
        glossary, memory = [], []
        result = audit_helper.audit([])
    _mysql_build_stage(bind)
    _mysql_build_audit(bind)
    _mysql_copy_stage(bind, audit_helper, glossary, memory, result)
    bind.exec_driver_sql(
        f'LOCK TABLES `project_glossaries` WRITE, `project_terminology_memory` READ, '
        f'`{_MYSQL_STAGE}` WRITE, `{_MYSQL_AUDIT}` WRITE, `projects` READ')
    try:
        _mysql_verify_stage(bind, helper, audit_helper, glossary, memory, result)
        count, digest = _mysql_backup_fingerprint(glossary)
        bind.exec_driver_sql(f'INSERT INTO `{_MYSQL_AUDIT}` (id, row_count, sha256) '
                             'VALUES (1, %s, %s)', (count, digest))
        _mysql_validate_audit(bind, helper, (count, digest))
        bind.exec_driver_sql(
            f'RENAME TABLE `project_glossaries` TO `{_MYSQL_BACKUP}`, '
            f'`{_MYSQL_STAGE}` TO `project_glossaries`')
    finally:
        bind.exec_driver_sql('UNLOCK TABLES')
    helper.validate_converted(bind)


def upgrade() -> None:
    bind = op.get_bind()
    helper = _helper('glossary_prerequisites.py')
    audit_helper = _helper('glossary_data_audit.py')
    if bind.dialect.name == 'mysql':
        _mysql_upgrade(bind, helper, audit_helper)
        return
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
