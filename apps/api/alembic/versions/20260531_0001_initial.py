"""initial: users + interest_tags

Revision ID: 20260531_0001
Revises:
Create Date: 2026-05-31

"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op


revision = "20260531_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(64), nullable=False, unique=True),
        sa.Column("display_avatar", sa.String(255)),
        sa.Column("birth_date", sa.Date),
        sa.Column("current_grade", sa.String(32)),
        sa.Column("interest_tags", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("theme", sa.String(64), server_default="default"),
        sa.Column("password_hash", sa.String(128), nullable=False),
        sa.Column("role", sa.String(16), server_default="kid"),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=False), server_default=sa.func.now()),
    )
    op.create_index("ix_users_name", "users", ["name"], unique=True)

    op.create_table(
        "interest_tags",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tag", sa.String(64), nullable=False),
        sa.Column("weight", sa.Integer, server_default="5"),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.func.now()),
    )
    op.create_index("ix_interest_tags_user_id", "interest_tags", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_interest_tags_user_id", "interest_tags")
    op.drop_table("interest_tags")
    op.drop_index("ix_users_name", "users")
    op.drop_table("users")
