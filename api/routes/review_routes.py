"""Data review & approval workflow routes."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import RATE_LIMIT_DEFAULT
from api.database import get_db
from api.deps import get_current_user, require_admin
from api.limiter import limiter
from api.models import DataReview, EmissionReport, ReviewStatus, User
from api.schemas import DataReviewAction, DataReviewCreate, DataReviewOut, PaginatedResponse
from api.services import audit

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=DataReviewOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def create_review(
    request: Request,
    body: DataReviewCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a review record for an emission report (starts in 'draft')."""
    # Verify report belongs to user's company
    result = await db.execute(
        select(EmissionReport).where(
            EmissionReport.id == body.report_id,
            EmissionReport.company_id == user.company_id,
            EmissionReport.deleted_at.is_(None),
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    # Prevent duplicate reviews for same report
    existing = await db.execute(
        select(DataReview).where(DataReview.report_id == body.report_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Review already exists for this report")

    review = DataReview(
        report_id=body.report_id,
        company_id=user.company_id,
        status=ReviewStatus.draft,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    await audit.record(
        db, user_id=user.id, company_id=user.company_id,
        action="create", resource_type="data_review", resource_id=review.id,
    )
    await db.commit()
    return review


@router.get("", response_model=PaginatedResponse[DataReviewOut])
@limiter.limit(RATE_LIMIT_DEFAULT)
async def list_reviews(
    request: Request,
    status_filter: str | None = None,
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List reviews for the current company, optionally filtered by status."""
    base = select(DataReview).where(DataReview.company_id == user.company_id)
    if status_filter:
        base = base.where(DataReview.status == status_filter)
    total_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(total_q)).scalar() or 0
    rows = (await db.execute(base.order_by(DataReview.created_at.desc()).offset(offset).limit(limit))).scalars().all()
    return {"items": rows, "total": total, "limit": limit, "offset": offset}


@router.get("/{review_id}", response_model=DataReviewOut)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def get_review(
    request: Request,
    review_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single review by ID."""
    review = await _get_review(db, review_id, user.company_id)
    return review


@router.post("/{review_id}/action", response_model=DataReviewOut)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def review_action(
    request: Request,
    review_id: str,
    body: DataReviewAction,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Perform an action on a review: submit, approve, or reject.

    State machine:
      draft → submitted (by any member)
      submitted → in_review (auto on approve/reject)
      submitted/in_review → approved (admin only)
      submitted/in_review → rejected (admin only)
    """
    review = await _get_review(db, review_id, user.company_id)
    now = datetime.now(timezone.utc)

    if body.action == "submit":
        if review.status not in (ReviewStatus.draft, ReviewStatus.rejected):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only submit from draft or rejected status")
        review.status = ReviewStatus.submitted
        review.submitted_by = user.id
        review.submitted_at = now
        review.reviewed_by = None
        review.reviewed_at = None
        review.review_notes = None

    elif body.action == "approve":
        if user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can approve reviews")
        if review.status not in (ReviewStatus.submitted, ReviewStatus.in_review):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only approve submitted or in-review items")
        review.status = ReviewStatus.approved
        review.reviewed_by = user.id
        review.reviewed_at = now
        review.review_notes = body.notes

    elif body.action == "reject":
        if user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can reject reviews")
        if review.status not in (ReviewStatus.submitted, ReviewStatus.in_review):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only reject submitted or in-review items")
        review.status = ReviewStatus.rejected
        review.reviewed_by = user.id
        review.reviewed_at = now
        review.review_notes = body.notes

    await audit.record(
        db, user_id=user.id, company_id=user.company_id,
        action=f"review_{body.action}", resource_type="data_review", resource_id=review.id,
        detail=body.notes,
    )
    await db.commit()
    await db.refresh(review)
    return review


# ── Helpers ─────────────────────────────────────────────────────────


async def _get_review(db: AsyncSession, review_id: str, company_id: str) -> DataReview:
    result = await db.execute(
        select(DataReview).where(
            DataReview.id == review_id,
            DataReview.company_id == company_id,
        )
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review
