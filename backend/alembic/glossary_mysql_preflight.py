"""Read-only collision probes using the database's own key comparison rules."""
import sqlalchemy as sa


def collision_codes(bind):
    """Reject cross-table ID equality and project spelling variants.

    The normalizer groups exact Python project IDs. A database collation may
    equate distinct strings (including trailing-space variants), so this probe
    must run before a MySQL conversion starts issuing DDL.
    """
    if bind.dialect.name == 'mysql':
        profiles = bind.execute(sa.text(
            "SELECT COLUMN_NAME, COUNT(*) AS n, "
            "COUNT(DISTINCT COLLATION_NAME) AS variants "
            "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() "
            "AND TABLE_NAME IN ('project_glossaries', 'project_terminology_memory') "
            "AND COLUMN_NAME IN ('id', 'project_id') GROUP BY COLUMN_NAME"
        )).mappings().all()
        if (len(profiles) != 2 or {row['COLUMN_NAME'] for row in profiles} != {'id', 'project_id'}
                or any(row['n'] != 2 or row['variants'] != 1 for row in profiles)):
            return ('COLLATION_MISMATCH',)
    glossary = sa.table('project_glossaries', sa.column('id'), sa.column('project_id'))
    memory = sa.table('project_terminology_memory', sa.column('id'), sa.column('project_id'))
    same_id = sa.select(sa.literal(1)).select_from(
        glossary.join(memory, glossary.c.id == memory.c.id)).limit(1)
    projects = sa.union_all(sa.select(glossary.c.project_id),
                            sa.select(memory.c.project_id)).subquery()
    variants = (sa.select(sa.literal(1)).select_from(projects)
                .group_by(projects.c.project_id)
                .having(sa.func.count(sa.distinct(
                    sa.cast(projects.c.project_id, sa.LargeBinary))) > 1)
                .limit(1))
    codes = []
    if bind.execute(same_id).first():
        codes.append('ID_COLLISION')
    if bind.execute(variants).first():
        codes.append('PROJECT_COLLATION_COLLISION')
    return tuple(codes)
