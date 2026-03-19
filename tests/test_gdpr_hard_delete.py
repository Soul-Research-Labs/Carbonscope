"""Tests for GDPR hard-delete (purge) endpoint."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient

from tests.conftest import TestSessionLocal

from sqlalchemy import select, text, update
from api.models import User, DataUpload, EmissionReport, _utcnow


@pytest.mark.asyncio
class TestGDPRHardDelete:
    """Admin-only permanent deletion of soft-deleted users."""

    async def _register_and_soft_delete(self, client: AsyncClient) -> str:
        """Register a second user, soft-delete them, return their id."""
        # Register a victim user in a new company
        resp = await client.post("/api/v1/auth/register", json={
            "email": "victim@example.com",
            "password": "Securepass123!",
            "full_name": "Victim User",
            "company_name": "VictimCorp",
            "industry": "energy",
            "region": "EU",
        })
        assert resp.status_code == 201
        user_id = resp.json()["id"]

        # Soft-delete: set deleted_at via DB
        async with TestSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one()
            user.deleted_at = _utcnow()
            user.is_active = False
            await session.commit()

        return user_id

    async def test_purge_soft_deleted_user(self, auth_client: AsyncClient):
        """Admin can permanently purge a soft-deleted user."""
        user_id = await self._register_and_soft_delete(auth_client)

        resp = await auth_client.delete(f"/api/v1/auth/users/{user_id}/purge")
        assert resp.status_code == 204

        # Verify user is gone
        async with TestSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            assert result.scalar_one_or_none() is None

    async def test_purge_non_existent_user_404(self, auth_client: AsyncClient):
        """Purging a non-existent user returns 404."""
        resp = await auth_client.delete("/api/v1/auth/users/nonexistent/purge")
        assert resp.status_code == 404

    async def test_purge_active_user_404(self, auth_client: AsyncClient):
        """Purging a user that hasn't been soft-deleted returns 404."""
        # Register but do NOT soft-delete
        resp = await auth_client.post("/api/v1/auth/register", json={
            "email": "active@example.com",
            "password": "Securepass123!",
            "full_name": "Active User",
            "company_name": "ActiveCorp",
            "industry": "energy",
            "region": "EU",
        })
        assert resp.status_code == 201
        user_id = resp.json()["id"]

        resp = await auth_client.delete(f"/api/v1/auth/users/{user_id}/purge")
        assert resp.status_code == 404

    async def test_purge_requires_auth(self, client: AsyncClient):
        """Unauthenticated request is rejected."""
        resp = await client.delete("/api/v1/auth/users/someid/purge")
        assert resp.status_code == 401

    async def test_purge_requires_admin(self, client: AsyncClient):
        """Non-admin user cannot purge."""
        # Register user (first user → admin by default)
        resp = await client.post("/api/v1/auth/register", json={
            "email": "member@example.com",
            "password": "Securepass123!",
            "full_name": "Member",
            "company_name": "MemberCorp",
            "industry": "manufacturing",
            "region": "US",
        })
        assert resp.status_code == 201
        user_id = resp.json()["id"]

        # Demote to member via DB
        async with TestSessionLocal() as session:
            await session.execute(
                update(User).where(User.id == user_id).values(role="member")
            )
            await session.commit()

        # Login as member
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "member@example.com",
            "password": "Securepass123!",
        })
        token = login_resp.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"

        resp = await client.delete("/api/v1/auth/users/someid/purge")
        assert resp.status_code == 403
