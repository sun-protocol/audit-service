import logging
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from app.database import SessionLocal
from app.models import Repository, ScanTask
from app.services.scanner import run_scan_sync

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=1)
_queue_lock = threading.Lock()
_task_queue: deque[dict] = deque()
_running_item: dict | None = None
_worker_running = False


def start_scheduler():
    logger.info("Background scan queue ready")


def shutdown_scheduler():
    _executor.shutdown(wait=False)


def trigger_scan(repo_id: int, triggered_by: str = "manual") -> int:
    db = SessionLocal()
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise ValueError(f"Repository {repo_id} not found")
        repo_url = repo.url
        task = ScanTask(repo_id=repo_id, status="pending", triggered_by=triggered_by)
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id
    finally:
        db.close()

    with _queue_lock:
        _task_queue.append(
            {
                "task_id": task_id,
                "repo_id": repo_id,
                "repo_url": repo_url,
                "triggered_by": triggered_by,
            }
        )

    _ensure_worker()
    return task_id
def get_queue_status() -> dict:
    with _queue_lock:
        running = dict(_running_item) if _running_item else None
        queued = [dict(item) for item in _task_queue]
    return {"running": running, "queued": queued}


def _ensure_worker():
    global _worker_running
    with _queue_lock:
        if _worker_running:
            return
        _worker_running = True
    _executor.submit(_queue_worker)


def _queue_worker():
    global _running_item, _worker_running
    while True:
        with _queue_lock:
            if not _task_queue:
                _running_item = None
                _worker_running = False
                return
            item = _task_queue.popleft()
            _running_item = dict(item)
        try:
            run_scan_sync(item["task_id"], SessionLocal)
        except Exception as e:
            logger.exception("Queued task execution failed: %s", e)
