"""
Scheduler core module for background job management.
Provides start/stop functions for APScheduler integration with FastAPI.
"""

import logging
from typing import Optional
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler

from airtools.components.scheduler.settings import (
    executors,
    jobstores,
    job_defaults,
)

logger = logging.getLogger(__name__)

# Module-level scheduler instance (singleton pattern)
_scheduler: Optional[BackgroundScheduler] = None


def get_scheduler() -> BackgroundScheduler:
    """
    Get or create the APScheduler instance.

    Returns:
        BackgroundScheduler: Configured scheduler instance
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=utc,
        )
    return _scheduler


def start_scheduler() -> None:
    """
    Start the background scheduler.
    Should be called during FastAPI lifespan startup.
    """
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started successfully")
    else:
        logger.warning("Scheduler already running")


def stop_scheduler() -> None:
    """
    Gracefully shutdown the scheduler.
    Should be called during FastAPI lifespan shutdown.
    """
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=True)
        logger.info("APScheduler shut down successfully")
        _scheduler = None


def add_scheduled_job(func, trigger: str, **trigger_kwargs):
    """
    Add a job to the scheduler.

    Args:
        func: Function to schedule
        trigger: Trigger type ('interval', 'cron', 'date')
        **trigger_kwargs: Trigger-specific arguments

    Returns:
        Job instance

    Example:
        add_scheduled_job(
            FetchData.collect_sensor_data,
            'interval',
            hours=1,
            kwargs={'sensor_uid': '88359', 'sensor_type': 'dht22'}
        )
    """
    scheduler = get_scheduler()
    job = scheduler.add_job(func, trigger, **trigger_kwargs)
    logger.info("Scheduled job: %s with trigger %s", func.__name__, trigger)
    return job
