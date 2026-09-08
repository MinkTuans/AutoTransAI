"""add workflow progress tracking columns

Revision ID: 20260908_workflow_progress
Revises: 20260908_youtube_progress
Create Date: 2026-09-08 09:26:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260908_workflow_progress'
down_revision = '20260908_youtube_progress'
branch_labels = None
depends_on = None

def upgrade() -> None:
    with op.batch_alter_table('workflow_executions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('overall_progress_pct', sa.Integer(), server_default='0', nullable=False))

    with op.batch_alter_table('workflow_stage_executions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('progress_percentage', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('current_item', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('total_items', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('message', sa.String(length=255), nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('workflow_stage_executions', schema=None) as batch_op:
        batch_op.drop_column('message')
        batch_op.drop_column('total_items')
        batch_op.drop_column('current_item')
        batch_op.drop_column('progress_percentage')

    with op.batch_alter_table('workflow_executions', schema=None) as batch_op:
        batch_op.drop_column('overall_progress_pct')
