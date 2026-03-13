import logging
import os
import subprocess
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from app.config import settings
from app.utils.crypto import decrypt_token

logger = logging.getLogger(__name__)


def _build_auth_url(url: str, token: str | None, platform: str) -> str:
    """Inject token into the clone URL for authentication."""
    if not token:
        return url
    parsed = urlparse(url)
    if platform == "gitlab":
        auth_url = f"{parsed.scheme}://oauth2:{token}@{parsed.netloc}{parsed.path}"
    else:
        auth_url = f"{parsed.scheme}://{token}@{parsed.netloc}{parsed.path}"
    return auth_url


def _repo_dir_name(url: str) -> str:
    """Derive a stable directory name from the repo URL."""
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_").replace(".git", "")
    return path or "repo"


def ensure_repo(
    url: str,
    branch: str,
    platform: str,
    encrypted_token: str | None,
    log: Callable[[str], None] | None = None,
) -> str:
    """Clone or pull the repository. Returns the local directory path."""
    token = decrypt_token(encrypted_token) if encrypted_token else None
    auth_url = _build_auth_url(url, token, platform)
    repo_dir = os.path.join(settings.WORKSPACES_DIR, _repo_dir_name(url))

    if os.path.isdir(os.path.join(repo_dir, ".git")):
        logger.info("Pulling latest for %s", url)
        if log:
            log(f"[Git] Pulling latest for {url}")
        _run_git(["git", "fetch", "--all"], cwd=repo_dir, log=log)
        _run_git(["git", "checkout", branch], cwd=repo_dir, log=log)
        _run_git(["git", "reset", "--hard", f"origin/{branch}"], cwd=repo_dir, log=log)
    else:
        logger.info("Cloning %s (branch=%s)", url, branch)
        if log:
            log(f"[Git] Cloning {url} (branch={branch})")
        Path(repo_dir).mkdir(parents=True, exist_ok=True)
        _run_git(
            ["git", "clone", "--branch", branch, "--single-branch", auth_url, repo_dir],
            log=log,
        )

    return repo_dir


def _run_git(cmd: list[str], cwd: str | None = None, log: Callable[[str], None] | None = None) -> str:
    if log:
        log(f"[Git] $ {' '.join(cmd)}")
    env = os.environ.copy()
    if settings.GIT_SSL_NO_VERIFY:
        env["GIT_SSL_NO_VERIFY"] = "true"
        if log:
            log("[Git] SSL verification disabled via GIT_SSL_NO_VERIFY")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if stdout and log:
        for line in stdout.splitlines():
            if line.strip():
                log(f"[Git] {line}")
    if stderr and log:
        for line in stderr.splitlines():
            if line.strip():
                log(f"[Git] {line}")
    if result.returncode != 0:
        raise RuntimeError(f"Git command failed: {stderr}")
    return stdout
