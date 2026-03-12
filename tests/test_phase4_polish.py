"""Phase 4 tests — password strength, enum types, schema validators, file upload."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient

from api.models import (
    AlertSeverity,
    AlertType,
    CreditReason,
    DataListingStatus,
    DataListingType,
    QuestionnaireStatus,
    QuestionStatus,
    ScenarioStatus,
    SubscriptionPlan,
    SubscriptionStatus,
    SupplyChainStatus,
    UserRole,
)
from api.schemas import (
    CompanyUpdate,
    SupplyChainLinkCreate,
    UserRegister,
    WebhookCreate,
)


# ── Enum value tests ────────────────────────────────────────────────


class TestEnums:
    def test_user_role_values(self):
        assert UserRole.admin.value == "admin"
        assert UserRole.member.value == "member"
        assert UserRole.admin == "admin"

    def test_supply_chain_status_values(self):
        assert set(s.value for s in SupplyChainStatus) == {"pending", "verified", "rejected"}

    def test_questionnaire_status_values(self):
        assert set(s.value for s in QuestionnaireStatus) == {
            "uploaded", "extracting", "extracted", "reviewed", "exported",
        }

    def test_question_status_values(self):
        assert set(s.value for s in QuestionStatus) == {"draft", "reviewed", "approved"}

    def test_scenario_status_values(self):
        assert set(s.value for s in ScenarioStatus) == {"draft", "computed", "archived"}

    def test_subscription_plan_values(self):
        assert set(p.value for p in SubscriptionPlan) == {"free", "pro", "enterprise"}

    def test_subscription_status_values(self):
        assert set(s.value for s in SubscriptionStatus) == {"active", "cancelled", "past_due"}

    def test_alert_type_values(self):
        assert "emission_increase" in [t.value for t in AlertType]

    def test_alert_severity_values(self):
        assert set(s.value for s in AlertSeverity) == {"info", "warning", "critical"}

    def test_data_listing_type_values(self):
        assert set(t.value for t in DataListingType) == {"emission_report", "benchmark", "supply_chain"}

    def test_data_listing_status_values(self):
        assert set(s.value for s in DataListingStatus) == {"active", "sold", "withdrawn"}

    def test_credit_reason_values(self):
        expected = {
            "subscription_grant", "plan_upgrade", "estimate_usage",
            "export_usage", "pdf_export_usage", "questionnaire_extract_usage",
            "scenario_compute_usage", "marketplace_purchase_usage",
            "manual", "manual_grant", "monthly_reset", "marketplace_sale",
            "plan_downgrade_adjustment",
        }
        assert set(r.value for r in CreditReason) == expected


# ── Password strength ──────────────────────────────────────────────


class TestPasswordStrength:
    def test_valid_password(self):
        user = UserRegister(
            email="a@b.com",
            password="Secure1!x",
            full_name="T",
            company_name="C",
            industry="tech",
        )
        assert user.password == "Secure1!x"

    def test_missing_special_char(self):
        with pytest.raises(Exception, match="special character"):
            UserRegister(
                email="a@b.com",
                password="Secure123",
                full_name="T",
                company_name="C",
                industry="tech",
            )

    def test_missing_lowercase(self):
        with pytest.raises(Exception, match="lowercase"):
            UserRegister(
                email="a@b.com",
                password="SECURE123!",
                full_name="T",
                company_name="C",
                industry="tech",
            )

    def test_missing_uppercase(self):
        with pytest.raises(Exception, match="uppercase"):
            UserRegister(
                email="a@b.com",
                password="secure123!",
                full_name="T",
                company_name="C",
                industry="tech",
            )

    def test_missing_digit(self):
        with pytest.raises(Exception, match="digit"):
            UserRegister(
                email="a@b.com",
                password="Securepass!",
                full_name="T",
                company_name="C",
                industry="tech",
            )

    @pytest.mark.anyio
    async def test_register_no_special_char_rejected(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "nospecial@test.com",
            "password": "Secure123",
            "full_name": "Test User",
            "company_name": "Corp",
            "industry": "tech",
        })
        assert resp.status_code == 422


# ── Schema validators ──────────────────────────────────────────────


class TestSchemaValidators:
    def test_company_update_negative_employee_count(self):
        with pytest.raises(Exception):
            CompanyUpdate(employee_count=-1)

    def test_company_update_negative_revenue(self):
        with pytest.raises(Exception):
            CompanyUpdate(revenue_usd=-100.0)

    def test_company_update_valid(self):
        cu = CompanyUpdate(employee_count=0, revenue_usd=0.0)
        assert cu.employee_count == 0

    def test_supply_chain_negative_spend(self):
        with pytest.raises(Exception):
            SupplyChainLinkCreate(supplier_company_id="abc", spend_usd=-50.0)

    def test_supply_chain_valid_spend(self):
        sc = SupplyChainLinkCreate(supplier_company_id="abc", spend_usd=100.0)
        assert sc.spend_usd == 100.0

    def test_webhook_invalid_url(self):
        with pytest.raises(Exception, match="https://|http://"):
            WebhookCreate(url="ftp://evil.com", event_types=["report.created"])

    def test_webhook_valid_url(self):
        w = WebhookCreate(url="https://hooks.example.com/cb", event_types=["report.created"])
        assert w.url.startswith("https://")
