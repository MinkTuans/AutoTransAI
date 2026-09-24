"""Frozen glossary normalization and lossless copy audit for Alembic.

The plan contains identifiers for internal use. Error codes alone are safe to
show to operators; raw terms and identifiers must stay out of exceptions.
"""
from collections import defaultdict
from dataclasses import dataclass
import unicodedata


def clean(value):
    value = unicodedata.normalize('NFKC', str(value or ''))
    value = ''.join(char for char in value
                    if unicodedata.category(char) not in {'Cf', 'Cc'} or char.isspace())
    return ' '.join(value.split())


def normalized(value):
    return clean(value).casefold()


@dataclass(frozen=True)
class Audit:
    conflict_codes: tuple[str, ...]
    import_ids: tuple[str, ...]


def audit(rows):
    """Select only unique memory mappings; reject any ambiguous state."""
    by_source = defaultdict(list)
    by_target = defaultdict(list)
    by_mapping = defaultdict(list)
    by_id = defaultdict(set)
    codes = set()
    for row in rows:
        table = row['table']
        identity = str(row['id'])
        source = clean(row['source_term'])
        target = clean(row['translated_term'])
        if not source or not target or len(source) > 255 or len(target) > 255:
            codes.add('INVALID_TERM')
        key = (str(row['project_id']), source.casefold(), target.casefold())
        by_source[key[:2]].append(key[2])
        by_target[(key[0], key[2])].append(key[1])
        by_mapping[key].append((table, identity))
        by_id[identity].add(table)

    if any(len(set(targets)) > 1 for targets in by_source.values()):
        codes.add('SOURCE_CONFLICT')
    if any(len(set(sources)) > 1 for sources in by_target.values()):
        codes.add('TRANSLATION_CONFLICT')
    if any(len(tables) > 1 for tables in by_id.values()):
        codes.add('ID_COLLISION')
    for records in by_mapping.values():
        for table, code in (('project_glossaries', 'DUPLICATE_GLOSSARY'),
                            ('project_terminology_memory', 'DUPLICATE_MEMORY')):
            if sum(name == table for name, _ in records) > 1:
                codes.add(code)
    if codes:
        return Audit(tuple(sorted(codes)), ())
    imports = [identity for records in by_mapping.values()
               if len(records) == 1
               for table, identity in records if table == 'project_terminology_memory']
    return Audit((), tuple(sorted(imports)))
