"""Phase 4: Enum columns (native_enum=False, no schema change) + doc-only.

Revision ID: d1e2f3a4b5c6
Revises: c9d4e5f6a7b8
Create Date: 2025-01-01 00:04:00.000000

Note: All Enum columns use native_enum=False, so the underlying VARCHAR columns
are unchanged. This migration exists to keep the Alembic chain consistent with
model changes introduced in Phase 4.
"""

from alembic import op

# revision identifiers
revision = "d1e2f3a4b5c6"
down_revision = "c9d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # native_enum=False stores enum values as plain strings in existing VARCHAR
    # columns — no DDL changes required.
    pass


def downgrade() -> None:
    pass
