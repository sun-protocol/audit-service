import argparse
import logging

from sqlalchemy import text

from app.database import Base, SessionLocal, engine
from app.models import Repository, ScanTask
from app.services.task_runner import create_repo_task_and_run_sync, create_task_and_run_sync, run_task_sync
from app.utils.crypto import encrypt_token


def _run_migrations():
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(repositories)"))
        columns = {row[1] for row in result}
        if "skill" not in columns:
            conn.execute(text("ALTER TABLE repositories ADD COLUMN skill VARCHAR(100)"))
            conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", type=int)
    parser.add_argument("--repo-id", type=int)
    parser.add_argument("--repo-url")
    parser.add_argument("--platform", default="github")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--access-token")
    parser.add_argument("--scan-prompt")
    parser.add_argument("--skill")
    parser.add_argument("--triggered-by", default="cli")
    args = parser.parse_args()

    if not args.task_id and not args.repo_id and not args.repo_url:
        parser.error("one of --task-id or --repo-id or --repo-url is required")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    Base.metadata.create_all(bind=engine)
    _run_migrations()

    if args.task_id:
        db = SessionLocal()
        try:
            task = db.query(ScanTask).filter(ScanTask.id == args.task_id).first()
            if not task:
                raise SystemExit(f"Task {args.task_id} not found")
            repo_name = task.repository.name if task.repository else str(task.repo_id)
            print(f"Running existing task {task.id} for repo {repo_name}")
        finally:
            db.close()
        run_task_sync(args.task_id, SessionLocal, log_hook=print, skill=args.skill)
        return

    if args.repo_url:
        print(f"Creating and running task for repo URL {args.repo_url}")
        task_id = create_repo_task_and_run_sync(
            url=args.repo_url,
            db_factory=SessionLocal,
            platform=args.platform,
            branch=args.branch,
            access_token_encrypted=encrypt_token(args.access_token) if args.access_token else None,
            scan_prompt=args.scan_prompt,
            triggered_by=args.triggered_by,
            log_hook=print,
            skill=args.skill,
        )
        print(f"Completed task {task_id}")
        return

    db = SessionLocal()
    try:
        repo = db.query(Repository).filter(Repository.id == args.repo_id).first()
        if not repo:
            raise SystemExit(f"Repository {args.repo_id} not found")
        print(f"Creating and running task for repo {repo.name} ({repo.id})")
    finally:
        db.close()

    task_id = create_task_and_run_sync(args.repo_id, SessionLocal, triggered_by=args.triggered_by, log_hook=print, skill=args.skill)
    print(f"Completed task {task_id}")


if __name__ == "__main__":
    main()
