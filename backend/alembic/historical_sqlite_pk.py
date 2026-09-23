"""Read-only SQLite identity checks for the frozen D1/D2 prerequisite tables.

Reflection exposes PK membership but omits collation, ordering, conflict policy,
and the distinction between an integer rowid alias and an indexed primary key.
This helper owns no schema definitions and must never import application code.
"""
import re

import sqlalchemy as sa


def _identifier(token):
    if token[:1] in ('"', "'", '`', '['):
        quote = ']' if token[0] == '[' else token[0]
        return token[1:-1].replace(quote * 2, quote)
    return token


def validate_primary_key(bind, table, mismatch):
    """Require the historical BINARY/ASC/ABORT identity, without probing writes."""
    indexes = bind.execute(sa.text('SELECT * FROM pragma_index_list(:table)'),
                           {'table': table.name}).mappings().all()
    primary = [index for index in indexes if index['origin'] == 'pk']
    integer = isinstance(table.c.id.type, sa.Integer)
    if integer:
        # INTEGER PRIMARY KEY aliases rowid and has no separate PK index.
        # INT PRIMARY KEY and column-level INTEGER PRIMARY KEY DESC do not.
        if primary:
            mismatch()
    else:
        if len(primary) != 1 or primary[0]['unique'] != 1 or primary[0]['partial'] != 0:
            mismatch()
        keys = bind.execute(sa.text(
            'SELECT name, "desc", coll FROM pragma_index_xinfo(:name) WHERE key = 1'),
            {'name': primary[0]['name']}).all()
        # SQLite preserves declared collation spelling in index_xinfo even
        # though collation names are case-insensitive. Keep name/order exact.
        normalized = [(name, order, coll.lower() if isinstance(coll, str) else coll)
                      for name, order, coll in keys]
        if normalized != [('id', 0, 'binary')]:
            mismatch()
    ddl = bind.execute(sa.text(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = :table"),
        {'table': table.name}).scalar_one()
    # Tokenize already-valid DDL only: quoted contents are opaque, comments are
    # discarded. This is not a general SQL parser or a schema reconstruction.
    tokens = [token.upper() for token in re.findall(
        r'''--[^\r\n]*|/\*.*?\*/|'(?:''|[^'])*'|"(?:""|[^"])*"|`(?:``|[^`])*`|\[[^\]]*\]|[A-Za-z_][A-Za-z_0-9$]*|\S''',
        ddl, re.DOTALL) if not token.startswith(('--', '/*'))]
    for offset, token in enumerate(tokens):
        if tokens[offset:offset + 2] == ['ON', 'CONFLICT']:
            # Frozen constraints all use default ABORT; accepting another
            # policy could conceal replacement even outside the PK clause.
            if tokens[offset + 2:offset + 3] != ['ABORT']:
                mismatch()
        if tokens[offset:offset + 2] == ['WITHOUT', 'ROWID'] or token == 'AUTOINCREMENT':
            mismatch()
    # Separate top-level declarations so the id column's comparison collation
    # cannot be hidden by a table PK that overrides its index to BINARY.
    clauses, clause, depth = [], [], 0
    for token in tokens[tokens.index('(') + 1:]:
        if depth == 0 and token in (',', ')'):
            clauses.append(clause)
            clause = []
            if token == ')':
                break
            continue
        depth += (token == '(') - (token == ')')
        clause.append(token)
    identity = [clause for clause in clauses if clause and _identifier(clause[0]) == 'ID']
    if len(identity) != 1:
        mismatch()
    for clause in clauses:
        table_pk = any(clause[i:i + 2] == ['PRIMARY', 'KEY'] for i in range(len(clause)))
        if clause not in identity and not table_pk:
            continue
        if 'DESC' in clause:
            mismatch()
        for offset, token in enumerate(clause):
            if token == 'COLLATE' and (offset + 1 == len(clause)
                                      or _identifier(clause[offset + 1]) != 'BINARY'):
                mismatch()
