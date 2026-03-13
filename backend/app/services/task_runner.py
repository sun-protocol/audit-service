import datetime
import logging
import subprocess
from typing import Callable

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Repository, ScanResult, ScanTask
from app.services.git_service import ensure_repo
from app.services.skill_service import prepare_skill_for_repo

logger = logging.getLogger(__name__)

_log_buffers: dict[int, list[str]] = {}


def get_log_buffer(task_id: int) -> list[str]:
    return _log_buffers.get(task_id, [])


def append_log(task_id: int, line: str):
    _log_buffers.setdefault(task_id, [])
    _log_buffers[task_id].append(line)
    if len(_log_buffers[task_id]) > 5000:
        _log_buffers[task_id] = _log_buffers[task_id][-3000:]


def run_task_sync(task_id: int, db_factory, log_hook: Callable[[str], None] | None = None, skill: str | None = None) -> None:
    db: Session = db_factory()
    try:
        task = db.query(ScanTask).filter(ScanTask.id == task_id).first()
        if not task:
            logger.error("Task %d not found", task_id)
            return

        repo: Repository = task.repository
        task.status = "running"
        task.started_at = datetime.datetime.utcnow()
        db.commit()

        def emit(line: str):
            append_log(task_id, line)
            if log_hook:
                log_hook(line)

        emit(f"[Audit Service] Starting scan for {repo.name} ({repo.url})")
        emit(f"[Audit Service] Branch: {repo.branch}")

        try:
            emit("[Audit Service] Syncing repository...")
            emit(f"[Git] Repository URL: {repo.url}")
            emit(f"[Git] Branch: {repo.branch}")
            repo_dir = ensure_repo(
                url=repo.url,
                branch=repo.branch,
                platform=repo.platform,
                encrypted_token=repo.access_token_encrypted,
            )
            emit(f"[Audit Service] Repository synced to {repo_dir}")
        except Exception as e:
            _finish_task(db, task, "failed", str(e), task_id, emit)
            return

        effective_skill = skill or (repo.skill if hasattr(repo, 'skill') else None)
        if effective_skill:
            try:
                emit(f"[Skill] Requested skill: {effective_skill}")
                skill_dir = prepare_skill_for_repo(repo_dir, effective_skill, log=emit)
                emit(f"[Skill] Skill ready at {skill_dir}")
            except Exception as e:
                _finish_task(db, task, "failed", str(e), task_id, emit)
                return

        if effective_skill:
            prompt = f"Use the {effective_skill} skill."
        else:
            prompt = repo.scan_prompt or settings.DEFAULT_SCAN_PROMPT
        cmd = [settings.OPENCODE_BIN, "run", "--format", "default", prompt]
        emit("[Audit Service] Executing: opencode run --format default ...")
        emit(f"[Audit Service] Working directory: {repo_dir}")
        emit(f"[Audit Service] Prompt: {prompt}")

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            output_lines: list[str] = []
            for line in iter(proc.stdout.readline, ""):
                line = line.rstrip("\n")
                output_lines.append(line)
                emit(line)
            proc.wait(timeout=1800)

            raw_output = "\n".join(output_lines)

            if proc.returncode != 0:
                _finish_task(db, task, "failed", raw_output, task_id, emit)
            else:
                _finish_task(db, task, "success", raw_output, task_id, emit)

        except subprocess.TimeoutExpired:
            proc.kill()
            _finish_task(db, task, "failed", "Scan timed out after 30 minutes", task_id, emit)
        except FileNotFoundError:
            _finish_task(db, task, "failed", f"opencode binary not found at: {settings.OPENCODE_BIN}", task_id, emit)
        except Exception as e:
            _finish_task(db, task, "failed", str(e), task_id, emit)

    finally:
        db.close()


def create_task_and_run_sync(repo_id: int, db_factory, triggered_by: str = "manual", log_hook: Callable[[str], None] | None = None, skill: str | None = None) -> int:
    db: Session = db_factory()
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise ValueError(f"Repository {repo_id} not found")
        task = ScanTask(repo_id=repo_id, status="pending", triggered_by=triggered_by)
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id
    finally:
        db.close()

    run_task_sync(task_id, db_factory, log_hook=log_hook, skill=skill)
    return task_id


def create_repo_task_and_run_sync(
    url: str,
    db_factory,
    platform: str = "github",
    branch: str = "main",
    access_token_encrypted: str | None = None,
    scan_prompt: str | None = None,
    triggered_by: str = "cli",
    log_hook: Callable[[str], None] | None = None,
    skill: str | None = None,
) -> int:
    db: Session = db_factory()
    try:
        repo = db.query(Repository).filter(Repository.url == url).first()
        if not repo:
            repo = Repository(
                name=_derive_repo_name(url),
                url=url,
                platform=platform,
                branch=branch,
                access_token_encrypted=access_token_encrypted,
                scan_prompt=scan_prompt,
            )
            db.add(repo)
            db.commit()
            db.refresh(repo)
        else:
            repo.platform = platform
            repo.branch = branch
            repo.scan_prompt = scan_prompt
            if access_token_encrypted:
                repo.access_token_encrypted = access_token_encrypted
            db.commit()
            db.refresh(repo)

        task = ScanTask(repo_id=repo.id, status="pending", triggered_by=triggered_by)
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id
    finally:
        db.close()

    run_task_sync(task_id, db_factory, log_hook=log_hook, skill=skill)
    return task_id


def _finish_task(db: Session, task: ScanTask, status: str, raw_output: str, task_id: int, emit: Callable[[str], None]):
    task.status = status
    task.finished_at = datetime.datetime.utcnow()
    if task.started_at:
        task.duration_seconds = (task.finished_at - task.started_at).total_seconds()

    result = db.query(ScanResult).filter(ScanResult.task_id == task.id).first()
    if result:
        result.raw_output = raw_output
        result.summary = _extract_summary(raw_output)
    else:
        result = ScanResult(
            task_id=task.id,
            raw_output=raw_output,
            summary=_extract_summary(raw_output),
        )
        db.add(result)
    db.commit()

    emit(f"[Audit Service] Scan finished with status: {status}")


def _extract_summary(raw_output: str) -> str:
    if len(raw_output) <= 500:
        return raw_output
    return raw_output[:500] + "..."


def _derive_repo_name(url: str) -> str:
    normalized = url.strip().rstrip("/")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    name = normalized.rsplit("/", 1)[-1].strip()
    return name or "repository"
