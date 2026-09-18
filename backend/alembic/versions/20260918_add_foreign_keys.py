"""Add missing foreign keys

Revision ID: 20260918_add_fk
Revises: 20260916_glossary_single_source
Create Date: 2026-09-18 17:52:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260918_add_fk'
down_revision: Union[str, None] = '20260916_glossary_single_source'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # We use batch_alter_table to support SQLite limitations

    # 1. workflow_engine -> projects
    with op.batch_alter_table("workflow_engine") as batch_op:
        batch_op.create_foreign_key("fk_workflow_engine_projects", "projects", ["project_id"], ["id"], ondelete="CASCADE")

    # 2. workflow_stages -> jobs (Assuming it links to something, actually let's skip unknown tables)
    # Based on the models modified earlier:
    
    # jobs -> projects
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.create_foreign_key("fk_jobs_projects", "projects", ["project_id"], ["id"], ondelete="CASCADE")

    # segments -> projects
    with op.batch_alter_table("segments") as batch_op:
        batch_op.create_foreign_key("fk_segments_projects", "projects", ["project_id"], ["id"], ondelete="CASCADE")

    # assets -> projects
    with op.batch_alter_table("assets") as batch_op:
        batch_op.create_foreign_key("fk_assets_projects", "projects", ["project_id"], ["id"], ondelete="CASCADE")

    # video_edit_configs -> projects, jobs
    with op.batch_alter_table("video_edit_configs") as batch_op:
        batch_op.create_foreign_key("fk_vec_projects", "projects", ["project_id"], ["id"], ondelete="CASCADE")
        batch_op.create_foreign_key("fk_vec_jobs", "jobs", ["job_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    with op.batch_alter_table("video_edit_configs") as batch_op:
        batch_op.drop_constraint("fk_vec_jobs", type_="foreignkey")
        batch_op.drop_constraint("fk_vec_projects", type_="foreignkey")

    with op.batch_alter_table("assets") as batch_op:
        batch_op.drop_constraint("fk_assets_projects", type_="foreignkey")

    with op.batch_alter_table("segments") as batch_op:
        batch_op.drop_constraint("fk_segments_projects", type_="foreignkey")

    with op.batch_alter_table("jobs") as batch_op:
        batch_op.drop_constraint("fk_jobs_projects", type_="foreignkey")

    with op.batch_alter_table("workflow_engine") as batch_op:
        batch_op.drop_constraint("fk_workflow_engine_projects", type_="foreignkey")
