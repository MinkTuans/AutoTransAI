"""Migration-owned glossary audit; no application imports or database writes."""
from pathlib import Path

from alembic.util import load_python_file


def audit(rows):
    helper = load_python_file(str(Path(__file__).parents[1] / 'alembic'),
                              'glossary_data_audit.py')
    return helper.audit(rows)


def row(table, row_id, source, target, project='p1'):
    return dict(table=table, id=row_id, project_id=project,
                source_term=source, translated_term=target)


def test_cross_table_equivalent_mapping_keeps_memory_and_needs_no_copy():
    result = audit([row('project_glossaries', 'g1', ' Ａ\u200b ', ' X '),
                    row('project_terminology_memory', 'm1', 'a', 'x')])
    assert result.conflict_codes == ()
    assert result.import_ids == ()


def test_distinct_memory_mapping_is_selected_for_copy():
    result = audit([row('project_glossaries', 'g1', 'A', 'X'),
                    row('project_terminology_memory', 'm1', 'B', 'Y')])
    assert result.conflict_codes == ()
    assert result.import_ids == ('m1',)


def test_conflicts_do_not_expose_private_terms_or_ids():
    result = audit([row('project_glossaries', 'private-id', 'private-source', 'private-a'),
                    row('project_terminology_memory', 'other-id', 'PRIVATE-SOURCE', 'private-b')])
    assert result.conflict_codes == ('SOURCE_CONFLICT',)
    assert 'private' not in repr(result.conflict_codes)
    assert result.import_ids == ()


def test_duplicate_glossary_mapping_cannot_be_collapsed_by_deleting_rows():
    result = audit([row('project_glossaries', 'g1', 'A', 'X'),
                    row('project_glossaries', 'g2', 'a', 'x')])
    assert result.conflict_codes == ('DUPLICATE_GLOSSARY',)
    assert result.import_ids == ()


def test_duplicate_memory_mapping_requires_reconciliation():
    result = audit([row('project_terminology_memory', 'm1', 'A', 'X'),
                    row('project_terminology_memory', 'm2', 'a', 'x')])
    assert result.conflict_codes == ('DUPLICATE_MEMORY',)
    assert result.import_ids == ()


def test_same_id_in_both_tables_cannot_be_copied():
    result = audit([row('project_glossaries', 'id1', 'A', 'X'),
                    row('project_terminology_memory', 'id1', 'B', 'Y')])
    assert result.conflict_codes == ('ID_COLLISION',)
    assert result.import_ids == ()


def test_normalized_empty_and_expanded_text_cannot_enter_canonical_glossary():
    result = audit([row('project_terminology_memory', 'm1', '\u200b', 'X'),
                    row('project_terminology_memory', 'm2', 'Ａ' * 256, 'Y')])
    assert result.conflict_codes == ('INVALID_TERM',)
    assert result.import_ids == ()
