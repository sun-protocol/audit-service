import json
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from app.config import settings

SKILLS_REPO_URL = "https://github.com/sun-protocol/sunagent-skills.git"


def prepare_skill_for_repo(repo_dir: str, skill_name: str, log: Callable[[str], None] | None = None) -> str:
    cache_repo_dir = Path(settings.SKILLS_CACHE_DIR) / "sunagent-skills"
    target_skill_dir = Path(repo_dir) / ".opencode" / "skills" / skill_name

    _sync_skills_repo(cache_repo_dir, log=log)

    source_skill_dir = _find_skill_dir(cache_repo_dir, skill_name)
    if not source_skill_dir:
        raise RuntimeError(f"Skill '{skill_name}' not found in {SKILLS_REPO_URL}")

    target_skill_dir.parent.mkdir(parents=True, exist_ok=True)
    if target_skill_dir.exists():
        shutil.rmtree(target_skill_dir)
    shutil.copytree(source_skill_dir, target_skill_dir)

    _ensure_opencode_permissions(repo_dir)
    if log:
        log(f"[Skill] Prepared skill '{skill_name}' at {target_skill_dir}")
    return str(target_skill_dir)


def _sync_skills_repo(cache_repo_dir: Path, log: Callable[[str], None] | None = None) -> None:
    cache_repo_dir.parent.mkdir(parents=True, exist_ok=True)
    if (cache_repo_dir / ".git").is_dir():
        if log:
            log(f"[Skill] Updating skills repo {SKILLS_REPO_URL}")
        _run(["git", "-C", str(cache_repo_dir), "fetch", "--all"], log=log)
        _run(["git", "-C", str(cache_repo_dir), "reset", "--hard", "origin/main"], log=log)
    else:
        if log:
            log(f"[Skill] Cloning skills repo {SKILLS_REPO_URL}")
        _run(["git", "clone", SKILLS_REPO_URL, str(cache_repo_dir)], log=log)


def _find_skill_dir(cache_repo_dir: Path, skill_name: str) -> Path | None:
    direct = cache_repo_dir / skill_name
    if (direct / "SKILL.md").is_file():
        return direct

    for path in cache_repo_dir.rglob("SKILL.md"):
        if path.parent.name == skill_name:
            return path.parent
    return None


def _ensure_opencode_permissions(repo_dir: str) -> None:
    config_path = Path(repo_dir) / "opencode.json"
    config: dict = {}
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
        except Exception:
            config = {}

    permission = config.setdefault("permission", {})
    skill = permission.setdefault("skill", {})
    skill["*"] = "allow"

    config_path.write_text(json.dumps(config, indent=2))


def _run(cmd: list[str], log: Callable[[str], None] | None = None) -> None:
    if log:
        log(f"[Skill] $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if stdout and log:
        for line in stdout.splitlines():
            if line.strip():
                log(f"[Skill] {line}")
    if stderr and log:
        for line in stderr.splitlines():
            if line.strip():
                log(f"[Skill] {line}")
    if result.returncode != 0:
        raise RuntimeError(stderr or f"Command failed: {' '.join(cmd)}")
