"""APScheduler ile periyodik olay izleme (opsiyonel).

Varsayilan olarak kapalidir: `YRKDS_MONITOR=1` ile acilir.
"""
from __future__ import annotations

import os

from apscheduler.schedulers.background import BackgroundScheduler

_scheduler: BackgroundScheduler | None = None


def baslat() -> BackgroundScheduler | None:
    global _scheduler
    if os.getenv("YRKDS_MONITOR") != "1" or _scheduler is not None:
        return _scheduler
    from app.ai.event_monitor import son_depremler

    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(son_depremler, "interval", minutes=15, id="deprem_izleme")
    _scheduler.start()
    return _scheduler


def durdur() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
