import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Repository, ScanTask
from app.schemas import DashboardStats, QueueItemOut, QueueStatusOut
from app.services.scheduler import get_queue_status

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    total_repos = db.query(Repository).count()
    enabled_repos = total_repos
    total_scans = db.query(ScanTask).count()

    now = datetime.datetime.utcnow()
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    scans_this_month = db.query(ScanTask).filter(ScanTask.started_at >= first_of_month).count()

    success_count = db.query(ScanTask).filter(ScanTask.status == "success").count()
    failed_count = db.query(ScanTask).filter(ScanTask.status == "failed").count()
    running_count = db.query(ScanTask).filter(ScanTask.status.in_(["pending", "running"])).count()

    return DashboardStats(
        total_repos=total_repos,
        enabled_repos=enabled_repos,
        total_scans=total_scans,
        scans_this_month=scans_this_month,
        success_count=success_count,
        failed_count=failed_count,
        running_count=running_count,
    )


@router.get("/queue", response_model=QueueStatusOut)
def get_dashboard_queue():
    status = get_queue_status()
    return QueueStatusOut(
        running=QueueItemOut(**status["running"]) if status["running"] else None,
        queued=[QueueItemOut(**item) for item in status["queued"]],
    )
