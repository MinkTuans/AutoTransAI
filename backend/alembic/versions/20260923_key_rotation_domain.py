"""Add safe canonical key rotation metadata and merge the two catalog heads."""
from alembic import op
import sqlalchemy as sa

revision = "20260923_key_rotation_domain"
down_revision = ("20260923_provider_key_requirement", "20260923_thumbnail_model_length")
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("api_keys", sa.Column("priority", sa.Integer(), nullable=False, server_default="100"))
    op.add_column("api_keys", sa.Column("runtime_status", sa.String(20), nullable=False, server_default="ready"))
    op.add_column("api_keys", sa.Column("cooldown_until", sa.DateTime(), nullable=True))
    op.add_column("api_keys", sa.Column("last_error_code", sa.String(32), nullable=True))
    op.add_column("api_keys", sa.Column("request_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("api_keys", sa.Column("success_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("api_keys", sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"))
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        # SQLite cannot add a CHECK without rebuilding the referenced key table.
        # A rebuild would fail or remove existing key-model access rows with FKs on.
        invalid = ("NEW.priority < 1 OR NEW.request_count < 0 OR NEW.success_count < 0 "
                   "OR NEW.failure_count < 0 OR NEW.runtime_status NOT IN "
                   "('ready', 'rate_limited', 'invalid', 'exhausted') OR "
                   "(NEW.last_error_code IS NOT NULL AND NEW.last_error_code NOT IN "
                   "('auth', 'quota', 'rate_limit', 'timeout', 'provider_unavailable', "
                   "'model_unavailable', 'capability_mismatch', 'invalid_output'))")
        for event in ("INSERT", "UPDATE"):
            op.execute(sa.text(
                f"CREATE TRIGGER ck_api_keys_rotation_{event.lower()} BEFORE {event} ON api_keys "
                f"FOR EACH ROW WHEN {invalid} BEGIN SELECT RAISE(ABORT, 'Invalid key rotation metadata'); END"
            ))
    else:
        op.create_check_constraint("ck_api_keys_priority_positive", "api_keys", "priority > 0")
        op.create_check_constraint("ck_api_keys_counters_nonnegative", "api_keys",
                                   "request_count >= 0 AND success_count >= 0 AND failure_count >= 0")
        op.create_check_constraint("ck_api_keys_runtime_status", "api_keys",
                                   "runtime_status IN ('ready', 'rate_limited', 'invalid', 'exhausted')")
        op.create_check_constraint("ck_api_keys_last_error_code", "api_keys",
                                   "last_error_code IS NULL OR last_error_code IN ('auth', 'quota', 'rate_limit', 'timeout', 'provider_unavailable', 'model_unavailable', 'capability_mismatch', 'invalid_output')")


def downgrade():
    # Metadata is dropped only on explicit administrative rollback.
    if op.get_bind().dialect.name == "sqlite":
        op.execute("DROP TRIGGER ck_api_keys_rotation_insert")
        op.execute("DROP TRIGGER ck_api_keys_rotation_update")
    else:
        for name in ("ck_api_keys_last_error_code", "ck_api_keys_runtime_status",
                     "ck_api_keys_counters_nonnegative", "ck_api_keys_priority_positive"):
            op.drop_constraint(name, "api_keys", type_="check")
    for column in ("failure_count", "success_count", "request_count", "last_error_code",
                   "cooldown_until", "runtime_status", "priority"):
        op.drop_column("api_keys", column)
