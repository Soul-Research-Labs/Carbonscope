"""Background task scheduler for periodic monitoring.

Uses asyncio tasks running within the FastAPI lifespan.
Checks alerts and sends email notifications on a configurable interval.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import async_session
from api.models import Company
from api.services.alerts import check_company_alerts

logger = logging.getLogger(__name__)

_scheduler_task: asyncio.Task | None = None

# Check interval in seconds (default: 1 hour)
CHECK_INTERVAL_SECONDS = 3600


async def _run_periodic_checks() -> None:
    """Background loop that checks all companies for alerts."""
    while True:
        try:
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)
            logger.info("Running periodic alert checks...")

            async with async_session() as db:
                result = await db.execute(select(Company.id))
                company_ids = [row[0] for row in result.all()]

                total_alerts = 0
                for company_id in company_ids:
                    try:
                        new_alerts = await check_company_alerts(db, company_id)
                        total_alerts += len(new_alerts)
                    except Exception:
                        logger.exception("Alert check failed for company %s", company_id)

                if total_alerts > 0:
                    await db.commit()
                    logger.info("Created %d new alerts across %d companies", total_alerts, len(company_ids))
                else:
                    logger.debug("No new alerts for %d companies", len(company_ids))

        except asyncio.CancelledError:
            logger.info("Scheduler shutting down")
            break
        except Exception:
            logger.exception("Scheduler error — will retry next cycle")


def start_scheduler() -> None:
    """Start the background scheduler task."""
    global _scheduler_task
    if _scheduler_task is None or _scheduler_task.done():
        _scheduler_task = asyncio.create_task(_run_periodic_checks())
        logger.info("Background scheduler started (interval=%ds)", CHECK_INTERVAL_SECONDS)


async def stop_scheduler() -> None:
    """Stop the background scheduler task."""
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
        _scheduler_task = None
        logger.info("Background scheduler stopped")
