from app.services.task_runner import append_log, get_log_buffer, run_task_sync


def run_scan_sync(task_id: int, db_factory) -> None:
    run_task_sync(task_id, db_factory)
