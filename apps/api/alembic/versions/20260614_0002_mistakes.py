"""mistakes + images + tags + error_tags + solution_hints

Revision ID: 20260614_0002
Revises: 20260531_0001
Create Date: 2026-06-14

"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op


revision = "20260614_0002"
down_revision = "20260531_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mistakes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject", sa.String(32), nullable=False),
        sa.Column("question_type", sa.String(32)),
        sa.Column("stem_text", sa.Text, server_default=""),
        sa.Column("stem_normalized", sa.Text),
        sa.Column("options", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("correct_answer", sa.Text),
        sa.Column("child_answer", sa.Text),
        sa.Column("knowledge_point_id", sa.Integer),
        sa.Column("error_hypothesis", sa.Text),
        sa.Column("grade", sa.Integer),
        sa.Column("occurred_at", sa.Date),
        sa.Column("srs_state", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("mastery_score", sa.Float, server_default="0"),
        sa.Column("is_golden", sa.Boolean, server_default=sa.false()),
        sa.Column("status", sa.String(16), server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=False), server_default=sa.func.now()),
    )
    op.create_index("ix_mistakes_user_id", "mistakes", ["user_id"])
    op.create_index("ix_mistakes_subject", "mistakes", ["subject"])
    op.create_index("ix_mistakes_grade", "mistakes", ["grade"])
    op.create_index("ix_mistakes_status", "mistakes", ["status"])
    op.create_index("ix_mistakes_knowledge_point_id", "mistakes", ["knowledge_point_id"])
    # 题干全文检索（pg_trgm）
    op.execute(
        "CREATE INDEX ix_mistakes_stem_trgm ON mistakes USING gin (stem_text gin_trgm_ops)"
    )

    op.create_table(
        "mistake_images",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("mistake_id", sa.Integer, sa.ForeignKey("mistakes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("object_key", sa.String(512), nullable=False),
        sa.Column("image_type", sa.String(32), server_default="original"),
        sa.Column("order", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.func.now()),
    )
    op.create_index("ix_mistake_images_mistake_id", "mistake_images", ["mistake_id"])

    op.create_table(
        "error_tags",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("mistake_id", sa.Integer, sa.ForeignKey("mistakes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tag", sa.String(64), nullable=False),
        sa.Column("source", sa.String(16), server_default="ai"),
    )
    op.create_index("ix_error_tags_mistake_id", "error_tags", ["mistake_id"])

    op.create_table(
        "mistake_tags",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("mistake_id", sa.Integer, sa.ForeignKey("mistakes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tag", sa.String(64), nullable=False),
    )
    op.create_index("ix_mistake_tags_mistake_id", "mistake_tags", ["mistake_id"])

    op.create_table(
        "solution_hints",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("mistake_id", sa.Integer, sa.ForeignKey("mistakes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content_md", sa.Text, server_default=""),
        sa.Column("source", sa.String(16), server_default="ai"),
        sa.Column("url", sa.String(512)),
        sa.Column("order", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.func.now()),
    )
    op.create_index("ix_solution_hints_mistake_id", "solution_hints", ["mistake_id"])


def downgrade() -> None:
    op.drop_table("solution_hints")
    op.drop_table("mistake_tags")
    op.drop_table("error_tags")
    op.drop_table("mistake_images")
    op.execute("DROP INDEX IF EXISTS ix_mistakes_stem_trgm")
    op.drop_table("mistakes")
