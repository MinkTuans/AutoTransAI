"""Widen thumbnail model identity for exact discovered provider model IDs."""

from pathlib import Path

from alembic import op
from alembic.util import load_python_file
import sqlalchemy as sa

revision = "20260923_thumbnail_model_length"
down_revision = "20260923_catalog_evidence"
branch_labels = None
depends_on = None


def upgrade():
    if not op.get_context().as_sql:
        helper = load_python_file(str(Path(__file__).resolve().parents[1]),
                                  'thumbnail_prerequisites.py')
        state = helper.preflight(op.get_bind())
        if state == 'absent':
            helper.create_current(op.get_bind())
            return
        if state == 'current':
            return
    with op.batch_alter_table("video_thumbnails") as batch:
        batch.alter_column("model", existing_type=sa.String(100), type_=sa.String(255),
                           existing_nullable=False)


def downgrade():
    # MySQL narrowing may truncate; refuse if any catalog model exceeds the
    # historical limit. Never silently destroy model identity on rollback.
    count = op.get_bind().execute(sa.text(
        "SELECT COUNT(*) FROM video_thumbnails WHERE LENGTH(model) > 100"
    )).scalar_one()
    if count:
        raise RuntimeError("Cannot narrow thumbnail model IDs longer than 100 characters.")
    with op.batch_alter_table("video_thumbnails") as batch:
        batch.alter_column("model", existing_type=sa.String(255), type_=sa.String(100),
                           existing_nullable=False)
