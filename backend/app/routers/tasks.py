import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models import Repository, ScanResult, ScanTask
from app.schemas import ResultOut, TaskDetailOut, TaskOut
from app.services.git_service import _repo_dir_name
from app.services.task_runner import get_log_buffer

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
def list_tasks(
    repo_id: int | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(ScanTask).join(Repository)
    if repo_id:
        q = q.filter(ScanTask.repo_id == repo_id)
    if status:
        q = q.filter(ScanTask.status == status)
    tasks = q.order_by(ScanTask.id.desc()).offset(offset).limit(limit).all()
    return [_task_to_out(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskDetailOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(ScanTask).filter(ScanTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    out = _task_to_out(task)
    result = db.query(ScanResult).filter(ScanResult.task_id == task_id).first()
    detail = TaskDetailOut(**out.model_dump(), result=ResultOut.model_validate(result) if result else None)
    return detail


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(ScanTask).filter(ScanTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()


@router.get("/{task_id}/logs")
async def stream_logs(task_id: int, db: Session = Depends(get_db)):
    task = db.query(ScanTask).filter(ScanTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    async def event_generator():
        sent = 0
        while True:
            buf = get_log_buffer(task_id)
            if len(buf) > sent:
                for line in buf[sent:]:
                    yield f"data: {json.dumps({'log': line})}\n\n"
                sent = len(buf)

            # Check if task is done
            db_check = next(get_db_gen())
            t = db_check.query(ScanTask).filter(ScanTask.id == task_id).first()
            db_check.close()
            if t and t.status in ("success", "failed"):
                # Send remaining logs
                buf = get_log_buffer(task_id)
                if len(buf) > sent:
                    for line in buf[sent:]:
                        yield f"data: {json.dumps({'log': line})}\n\n"
                yield f"data: {json.dumps({'status': t.status, 'done': True})}\n\n"
                break

            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/{task_id}/audit-report")
def download_audit_report(task_id: int, db: Session = Depends(get_db)):
    task = db.query(ScanTask).filter(ScanTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    repo_workspace = Path(settings.WORKSPACES_DIR) / _repo_dir_name(task.repository.url)
    candidate = repo_workspace / ".audit" / "Audit-Report.md"
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="Audit report not found")

    return FileResponse(
        path=str(candidate),
        media_type="text/markdown",
        filename=f"audit-report-task-{task.id}.md",
    )


def get_db_gen():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _task_to_out(task: ScanTask) -> TaskOut:
    return TaskOut(
        id=task.id,
        repo_id=task.repo_id,
        repo_name=task.repository.name if task.repository else None,
        repo_url=task.repository.url if task.repository else None,
        status=task.status,
        started_at=task.started_at,
        finished_at=task.finished_at,
        duration_seconds=task.duration_seconds,
    )
