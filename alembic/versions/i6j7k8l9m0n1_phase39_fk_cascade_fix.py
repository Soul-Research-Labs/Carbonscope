"""Phase 39: Add ondelete SET NULL to EmissionReport.data_upload_id FK

Revision ID: i6j7k8l9m0n1
Revises: h5i6j7k8l9m0
Create Date: 2026-03-14 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "i6j7k8l9m0n1"
down_revision = "h5i6j7k8l9m0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("emission_reports") as batch_op:
        batch_op.drop_constraint("fk_emission_reports_data_upload_id", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_emission_reports_data_upload_id",
            "data_uploads",
            ["data_upload_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("emission_reports") as batch_op:
        batch_op.drop_constraint("fk_emission_reports_data_upload_id", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_emission_reports_data_upload_id",
            "data_uploads",
            ["data_upload_id"],
            ["id"],
        )
