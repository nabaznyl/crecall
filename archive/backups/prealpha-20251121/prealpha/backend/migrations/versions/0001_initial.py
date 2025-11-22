"""Initial schema creation for crecall.

Revision ID: 0001_initial
Revises: 
Create Date: 2025-11-21
"""
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("theme_preference", sa.String(10), nullable=False, server_default="dark"),
    )
    op.create_index("ix_sessions_status_created", "sessions", ["status", "created_at"])

    op.create_table(
        "clips",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("clip_id", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200)),
        sa.Column("is_auto", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("content", sa.JSON, nullable=False),
        sa.Column("working_directory", sa.String(500)),
        sa.Column("git_branch", sa.String(200)),
        sa.Column("git_commit", sa.String(40)),
        sa.Column("git_dirty", sa.Boolean, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_clips_session_created", "clips", ["session_id", "created_at"])

    op.create_table(
        "checkpoints",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("note", sa.Text),
        sa.Column("working_directory", sa.String(500)),
        sa.Column("docker_context", sa.String(100)),
        sa.Column("extra_data", sa.JSON),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_checkpoints_session_created", "checkpoints", ["session_id", "created_at"])

    op.create_table(
        "memories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("tags", sa.JSON),
        sa.Column("category", sa.String(100)),
        sa.Column("importance", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("linked_clip_id", sa.Integer, sa.ForeignKey("clips.id")),
        sa.Column("linked_checkpoint_id", sa.Integer, sa.ForeignKey("checkpoints.id")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_memories_session_created", "memories", ["session_id", "created_at"])
    op.create_index("ix_memories_importance", "memories", ["importance"])


def downgrade():
    op.drop_index("ix_memories_importance", table_name="memories")
    op.drop_index("ix_memories_session_created", table_name="memories")
    op.drop_table("memories")
    op.drop_index("ix_checkpoints_session_created", table_name="checkpoints")
    op.drop_table("checkpoints")
    op.drop_index("ix_clips_session_created", table_name="clips")
    op.drop_table("clips")
    op.drop_index("ix_sessions_status_created", table_name="sessions")
    op.drop_table("sessions")
