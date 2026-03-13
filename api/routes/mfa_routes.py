"""MFA (Multi-Factor Authentication) routes — TOTP setup, verify, disable."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import RATE_LIMIT_AUTH
from api.database import get_db
from api.deps import get_current_user
from api.limiter import limiter
from api.models import MFASecret, User
from api.schemas import MFASetupOut, MFAStatusOut, MFAVerifyRequest
from api.services.mfa import (
    build_provisioning_uri,
    generate_backup_codes,
    generate_totp_secret,
    hash_backup_code,
    verify_totp,
)
from api.services import audit

router = APIRouter(prefix="/auth/mfa", tags=["mfa"])


@router.get("/status", response_model=MFAStatusOut)
@limiter.limit(RATE_LIMIT_AUTH)
async def mfa_status(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check whether MFA is enabled for the current user."""
    result = await db.execute(
        select(MFASecret).where(MFASecret.user_id == user.id)
    )
    secret_row = result.scalar_one_or_none()
    return {"mfa_enabled": secret_row is not None and secret_row.is_enabled}


@router.post("/setup", response_model=MFASetupOut)
@limiter.limit(RATE_LIMIT_AUTH)
async def setup_mfa(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate TOTP secret and backup codes. MFA is not active until /verify is called."""
    # Check if already enabled
    result = await db.execute(
        select(MFASecret).where(MFASecret.user_id == user.id)
    )
    existing = result.scalar_one_or_none()
    if existing and existing.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="MFA is already enabled. Disable it first to reconfigure.",
        )

    secret = generate_totp_secret()
    backup_codes = generate_backup_codes()
    hashed_codes = json.dumps([hash_backup_code(c) for c in backup_codes])
    uri = build_provisioning_uri(secret, user.email)

    if existing:
        # Overwrite pending (not-yet-enabled) setup
        existing.totp_secret = secret
        existing.backup_codes = hashed_codes
        existing.is_enabled = False
    else:
        db.add(MFASecret(
            user_id=user.id,
            totp_secret=secret,
            backup_codes=hashed_codes,
            is_enabled=False,
        ))

    await db.commit()

    await audit.record(
        db, user_id=user.id, company_id=user.company_id,
        action="mfa_setup", resource_type="mfa", resource_id=str(user.id),
    )
    await db.commit()

    return {
        "secret": secret,
        "provisioning_uri": uri,
        "backup_codes": backup_codes,
    }


@router.post("/verify", response_model=MFAStatusOut)
@limiter.limit(RATE_LIMIT_AUTH)
async def verify_and_enable_mfa(
    request: Request,
    body: MFAVerifyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify a TOTP code to activate MFA. Must call /setup first."""
    result = await db.execute(
        select(MFASecret).where(MFASecret.user_id == user.id)
    )
    secret_row = result.scalar_one_or_none()
    if not secret_row:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Call /setup first")

    if not verify_totp(secret_row.totp_secret, body.totp_code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")

    secret_row.is_enabled = True
    await db.commit()
    await audit.record(
        db, user_id=user.id, company_id=user.company_id,
        action="mfa_enabled", resource_type="mfa", resource_id=str(user.id),
    )
    await db.commit()
    return {"mfa_enabled": True}


@router.post("/validate", response_model=MFAStatusOut)
@limiter.limit(RATE_LIMIT_AUTH)
async def validate_totp(
    request: Request,
    body: MFAVerifyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate a TOTP code (used during login second factor)."""
    result = await db.execute(
        select(MFASecret).where(MFASecret.user_id == user.id, MFASecret.is_enabled.is_(True))
    )
    secret_row = result.scalar_one_or_none()
    if not secret_row:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled")

    if not verify_totp(secret_row.totp_secret, body.totp_code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")

    return {"mfa_enabled": True}


@router.delete("/disable", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(RATE_LIMIT_AUTH)
async def disable_mfa(
    request: Request,
    body: MFAVerifyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disable MFA — requires a valid TOTP code for confirmation."""
    result = await db.execute(
        select(MFASecret).where(MFASecret.user_id == user.id, MFASecret.is_enabled.is_(True))
    )
    secret_row = result.scalar_one_or_none()
    if not secret_row:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled")

    if not verify_totp(secret_row.totp_secret, body.totp_code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")

    await db.delete(secret_row)
    await db.commit()
    await audit.record(
        db, user_id=user.id, company_id=user.company_id,
        action="mfa_disabled", resource_type="mfa", resource_id=str(user.id),
    )
    await db.commit()
