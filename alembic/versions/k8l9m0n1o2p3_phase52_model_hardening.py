"""Phase 52: Model hardening — updated_at columns, cascades, indexes

Revision ID: k8l9m0n1o2p3
Revises: j7k8l9m0n1o2
Create Date: 2026-03-14

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "k8l9m0n1o2p3"
down_revision = "j7k8l9m0n1o2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- Add updated_at columns to models that were missing them --
    for table in (
        "data_uploads",
        "emission_reports",
        "supply_chain_links",
        "webhooks",
        "alerts",
        "data_listings",
        "financed_assets",
        "mfa_secrets",
    ):
        op.add_column(table, sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))

    # -- Add missing indexes --
    op.create_index("ix_supply_chain_links_status", "supply_chain_links", ["status"])
    op.create_index("ix_data_purchases_created_at", "data_purchases", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_data_purchases_created_at", table_name="data_purchases")
    op.drop_index("ix_supply_chain_links_status", table_name="supply_chain_links")

    for table in (
        "mfa_secrets",
        "financed_assets",
        "data_listings",
        "alerts",
        "webhooks",
        "supply_chain_links",
        "emission_reports",
        "data_uploads",
    ):
        op.drop_column(table, "updated_at")
