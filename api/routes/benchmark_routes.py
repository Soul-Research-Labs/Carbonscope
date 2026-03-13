"""Industry benchmarking routes — compare company emissions against peers."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import RATE_LIMIT_DEFAULT
from api.database import get_db
from api.deps import get_current_user
from api.limiter import limiter
from api.models import Company, EmissionReport, IndustryBenchmark, User
from api.schemas import BenchmarkComparison, BenchmarkOut, PaginatedResponse

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.get("", response_model=PaginatedResponse[BenchmarkOut])
@limiter.limit(RATE_LIMIT_DEFAULT)
async def list_benchmarks(
    request: Request,
    industry: str | None = None,
    region: str | None = None,
    year: int | None = None,
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List available industry benchmarks, optionally filtered."""
    base = select(IndustryBenchmark)
    if industry:
        base = base.where(IndustryBenchmark.industry == industry)
    if region:
        base = base.where(IndustryBenchmark.region == region)
    if year:
        base = base.where(IndustryBenchmark.year == year)

    total_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(total_q)).scalar() or 0
    rows = (await db.execute(
        base.order_by(IndustryBenchmark.year.desc(), IndustryBenchmark.industry).offset(offset).limit(limit)
    )).scalars().all()
    return {"items": rows, "total": total, "limit": limit, "offset": offset}


@router.get("/compare", response_model=BenchmarkComparison)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def compare_to_industry(
    request: Request,
    report_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compare a company's emission report against the industry benchmark."""
    # Fetch report
    result = await db.execute(
        select(EmissionReport).where(
            EmissionReport.id == report_id,
            EmissionReport.company_id == user.company_id,
            EmissionReport.deleted_at.is_(None),
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    # Fetch company for industry
    company_result = await db.execute(select(Company).where(Company.id == user.company_id))
    company = company_result.scalar_one()

    # Find the closest benchmark
    bench_result = await db.execute(
        select(IndustryBenchmark).where(
            IndustryBenchmark.industry == company.industry,
            IndustryBenchmark.year == report.year,
        ).order_by(
            # Prefer company's region, fall back to GLOBAL
            (IndustryBenchmark.region == company.region).desc(),
        ).limit(1)
    )
    benchmark = bench_result.scalar_one_or_none()

    company_emissions = {
        "scope1": report.scope1,
        "scope2": report.scope2,
        "scope3": report.scope3,
        "total": report.total,
    }

    if benchmark is None:
        return {
            "company_emissions": company_emissions,
            "industry_average": None,
            "percentile_rank": {"scope1": None, "scope2": None, "scope3": None, "total": None},
            "vs_average": {"scope1": None, "scope2": None, "scope3": None, "total": None},
        }

    def _pct_diff(company_val: float, avg_val: float) -> float:
        if avg_val == 0:
            return 0.0
        return round((company_val - avg_val) / avg_val * 100, 1)

    def _rank_label(pct_diff: float) -> str:
        if pct_diff <= -30:
            return "top_10"
        if pct_diff <= -10:
            return "top_25"
        if pct_diff <= 10:
            return "median"
        if pct_diff <= 30:
            return "bottom_25"
        return "bottom_10"

    vs = {
        "scope1": _pct_diff(report.scope1, benchmark.avg_scope1_tco2e),
        "scope2": _pct_diff(report.scope2, benchmark.avg_scope2_tco2e),
        "scope3": _pct_diff(report.scope3, benchmark.avg_scope3_tco2e),
        "total": _pct_diff(report.total, benchmark.avg_total_tco2e),
    }

    ranks = {k: _rank_label(v) for k, v in vs.items()}

    return {
        "company_emissions": company_emissions,
        "industry_average": benchmark,
        "percentile_rank": ranks,
        "vs_average": vs,
    }
