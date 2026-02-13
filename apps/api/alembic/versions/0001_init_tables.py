from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="merchant"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("merchant_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="usd"),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("stripe_checkout_session_id", sa.String(length=255)),
        sa.Column("stripe_payment_intent_id", sa.String(length=255)),
        sa.Column("customer_ref_enc", sa.String(length=2048)),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_payments_merchant_id", "payments", ["merchant_id"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_stripe_checkout_session_id", "payments", ["stripe_checkout_session_id"])
    op.create_index("ix_payments_stripe_payment_intent_id", "payments", ["stripe_payment_intent_id"])
    op.create_index("ix_payments_merchant_created", "payments", ["merchant_id", "created_at"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer()),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("resource", sa.String(length=120), nullable=False),
        sa.Column("ip", sa.String(length=64)),
        sa.Column("user_agent", sa.String(length=255)),
        sa.Column("details", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])

    op.create_table(
        "aml_alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("payment_id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("reasons", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_aml_alerts_payment_id", "aml_alerts", ["payment_id"])
    op.create_index("ix_aml_alerts_merchant_id", "aml_alerts", ["merchant_id"])
    op.create_index("ix_aml_alerts_score", "aml_alerts", ["score"])

def downgrade():
    op.drop_index("ix_aml_alerts_score", table_name="aml_alerts")
    op.drop_index("ix_aml_alerts_merchant_id", table_name="aml_alerts")
    op.drop_index("ix_aml_alerts_payment_id", table_name="aml_alerts")
    op.drop_table("aml_alerts")

    op.drop_index("ix_audit_logs_actor_user_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_payments_merchant_created", table_name="payments")
    op.drop_index("ix_payments_stripe_payment_intent_id", table_name="payments")
    op.drop_index("ix_payments_stripe_checkout_session_id", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_merchant_id", table_name="payments")
    op.drop_table("payments")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
