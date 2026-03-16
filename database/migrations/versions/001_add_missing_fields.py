"""Add missing pipeline and project fields; fix subscription counter type

Revision ID: 001_add_missing_fields
Revises:
Create Date: 2026-03-17

Changes:
  pipeline_runs : +repo_full_name (VARCHAR 255), +pr_number (INTEGER)
  projects      : +pr_comments_enabled (BOOLEAN), +auto_fix_enabled (BOOLEAN)
  subscriptions : runs_used_this_month VARCHAR(10) -> INTEGER
                  +billing_period_start (DATE)
  users         : +oauth_provider, +oauth_id, +avatar_url
"""
from alembic import op
import sqlalchemy as sa

revision = '001_add_missing_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── pipeline_runs ────────────────────────────────────────────────────────────────
    op.add_column("pipeline_runs", sa.Column("repo_full_name", sa.String(255), nullable=True))
    op.add_column("pipeline_runs", sa.Column("pr_number", sa.Integer(), nullable=True))

    # ─── projects ─────────────────────────────────────────────────────────────────────
    op.add_column("projects", sa.Column(
        "pr_comments_enabled", sa.Boolean(), nullable=False,
        server_default=sa.text("false"),
    ))
    op.add_column("projects", sa.Column(
        "auto_fix_enabled", sa.Boolean(), nullable=False,
        server_default=sa.text("false"),
    ))

    # ─── subscriptions ─────────────────────────────────────────────────────────────
    # Safely cast existing string values; COALESCE handles NULL/empty strings
    op.execute(
        "ALTER TABLE subscriptions "
        "ALTER COLUMN runs_used_this_month TYPE INTEGER "
        "USING CAST(COALESCE(NULLIF(runs_used_this_month, ''), '0') AS INTEGER)"
    )
    op.alter_column(
        "subscriptions", "runs_used_this_month",
        existing_type=sa.String(10),
        type_=sa.Integer(),
        nullable=False,
        server_default="0",
    )
    op.add_column("subscriptions", sa.Column("billing_period_start", sa.Date(), nullable=True))

    # ─── users ──────────────────────────────────────────────────────────────────────
    op.add_column("users", sa.Column("oauth_provider", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("oauth_id", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.String(500), nullable=True))
    # Allow empty password for OAuth-only users
    op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=False, server_default="")


def downgrade() -> None:
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "oauth_id")
    op.drop_column("users", "oauth_provider")
    op.drop_column("subscriptions", "billing_period_start")
    op.alter_column(
        "subscriptions", "runs_used_this_month",
        existing_type=sa.Integer(),
        type_=sa.String(10),
        nullable=True,
    )
    op.drop_column("projects", "auto_fix_enabled")
    op.drop_column("projects", "pr_comments_enabled")
    op.drop_column("pipeline_runs", "pr_number")
    op.drop_column("pipeline_runs", "repo_full_name")
