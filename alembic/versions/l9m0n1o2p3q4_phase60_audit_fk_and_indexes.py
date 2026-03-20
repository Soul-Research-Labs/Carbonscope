"""Phase 60: AuditLog FK cascade→SET NULL + deleted_at indexes

Revision ID: l9m0n1o2p3q4
Revises: k8l9m0n1o2p3
Create Date: 2026-03-20

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "l9m0n1o2p3q4"
down_revision = "k8l9m0n1o2p3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- AuditLog: change CASCADE to SET NULL so audit trail survives user/company deletion --
    with op.batch_alter_table("audit_logs") as batch:
        batch.drop_constraint("fk_audit_logs_user_id_users", type_="foreignkey")
        batch.drop_constraint("fk_audit_logs_company_id_companies", type_="foreignkey")
        batch.alter_column("user_id", nullable=True)
        batch.alter_column("company_id", nullable=True)
        batch.create_foreign_key(
            "fk_audit_logs_user_id_users",
            "users", ["user_id"], ["id"], ondelete="SET NULL",
        )
        batch.create_foreign_key(
            "fk_audit_logs_company_id_companies",
            "companies", ["company_id"], ["id"], ondelete="SET NULL",
        )

    # -- Add partial indexes on deleted_at for soft-delete query performance --
    for table in ("users", "companies", "emission_reports", "data_uploads", "questionnaires"):
        op.create_index(
            f"ix_{table}_active",
            table,
            ["deleted_at"],
            postgresql_where="deleted_at IS NULL",
        )


def downgrade() -> None:
    for table in ("users", "companies", "emission_reports", "data_uploads", "questionnaires"):
        op.drop_index(f"ix_{table}_active", table_name=table)

    with op.batch_alter_table("audit_logs") as batch:
        batch.drop_constraint("fk_audit_logs_user_id_users", type_="foreignkey")
        batch.drop_constraint("fk_audit_logs_company_id_companies", type_="foreignkey")
        batch.alter_column("user_id", nullable=False)
        batch.alter_column("company_id", nullable=False)
        batch.create_foreign_key(
            "fk_audit_logs_user_id_users",
            "users", ["user_id"], ["id"], ondelete="CASCADE",
        )
        batch.create_foreign_key(
            "fk_audit_logs_company_id_companies",
            "companies", ["company_id"], ["id"], ondelete="CASCADE",
        )
