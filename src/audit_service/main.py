import asyncio
import logging
import re
import shutil
import zipfile
from collections.abc import AsyncIterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import APIKeyHeader

from .auditor import run_audit, run_pr_audit
from .config import settings
from .html_converter import markdown_to_html
from .skill_loader import Skill, load_skills

logger = logging.getLogger(__name__)

REPORTS_DIR = Path("reports").resolve()
REPORTS_DIR.mkdir(exist_ok=True)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_executor = ThreadPoolExecutor(max_workers=4)


@lru_cache
def _cached_skills():
    return load_skills(settings.skills_dir)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    _cached_skills()
    logger.info("Loaded skills: %s", list(_cached_skills().keys()))
    yield
    _executor.shutdown(wait=False)


app = FastAPI(title="Code Audit Service", version="0.1.0", lifespan=lifespan)


async def verify_api_key(api_key: str | None = Depends(api_key_header)):
    """Verify the API key from X-API-Key header."""
    valid_keys = settings.get_api_keys()
    if not valid_keys:
        return
    if not api_key or api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def _sanitize_name(name: str) -> str:
    """Sanitize a string for safe use as a directory name."""
    return re.sub(r"[^\w\-.]", "_", name).strip("._")


# ---------------------------------------------------------------------------
# Background audit tasks
# ---------------------------------------------------------------------------

def _run_security_audit_background(
    skill: Skill,
    code_dir: Path,
    report_dir: Path,
    report_url: str,
) -> None:
    """Run security audit in background thread, write HTML report when done."""
    loop = asyncio.new_event_loop()
    try:
        agent_output = loop.run_until_complete(
            run_audit(skill=skill, code_dir=str(code_dir))
        )

        md_report = _resolve_report(skill, code_dir, report_dir, agent_output)
        html_content = markdown_to_html(
            md_report, title=f"Audit Report - {skill.name}"
        )
        html_path = report_dir / "audit-report.html"
        html_path.write_text(html_content, encoding="utf-8")
        logger.info("Security audit report saved: %s", report_url)
    except Exception:
        logger.exception("Background security audit failed: %s", report_url)
        _write_error_report(report_dir, "Security audit failed. See server logs.")
    finally:
        loop.close()


def _run_pr_audit_background(
    skill: Skill,
    code_dir: Path,
    report_dir: Path,
    report_url: str,
    from_branch: str,
    to_branch: str,
) -> None:
    """Run PR audit in background thread, write HTML report when done."""
    loop = asyncio.new_event_loop()
    try:
        agent_output = loop.run_until_complete(
            run_pr_audit(
                skill=skill,
                code_dir=str(code_dir),
                from_branch=from_branch,
                to_branch=to_branch,
            )
        )

        md_report = _resolve_report(skill, code_dir, report_dir, agent_output)
        html_content = markdown_to_html(
            md_report, title=f"PR Audit Report - {skill.name}"
        )
        html_path = report_dir / "audit-report.html"
        html_path.write_text(html_content, encoding="utf-8")
        logger.info("PR audit report saved: %s", report_url)
    except Exception:
        logger.exception("Background PR audit failed: %s", report_url)
        _write_error_report(report_dir, "PR audit failed. See server logs.")
    finally:
        loop.close()


def _resolve_report(
    skill: Skill,
    code_dir: Path,
    report_dir: Path,
    agent_output: str,
) -> str:
    """Find the skill-defined report file, fall back to agent output."""
    suffix = Path(skill.report_path)
    skill_report_file = next(
        (p for p in report_dir.rglob("*") if p.is_file() and p.match(f"*/{suffix}")),
        None,
    )
    if skill_report_file is not None:
        logger.info("Using report from %s", skill_report_file)
        return skill_report_file.read_text(encoding="utf-8")
    logger.info("Report file %s not found, using agent output", skill.report_path)
    return agent_output


def _write_error_report(report_dir: Path, message: str) -> None:
    """Write a minimal error HTML report so the status endpoint can detect failure."""
    html = markdown_to_html(f"# Audit Failed\n\n{message}", title="Audit Failed")
    (report_dir / "audit-report.html").write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _validate_and_extract_zip(
    content: bytes,
    report_dir: Path,
    code_dir: Path,
) -> None:
    """Save zip, validate paths, and extract. Raises HTTPException on error."""
    if len(content) > settings.max_upload_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_upload_size} bytes",
        )

    zip_path = report_dir / "upload.zip"
    zip_path.write_bytes(content)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                extracted = (code_dir / name).resolve()
                if not str(extracted).startswith(str(code_dir)):
                    raise HTTPException(
                        status_code=400, detail="Zip contains unsafe paths"
                    )
            zf.extractall(code_dir)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip file")


# ---------------------------------------------------------------------------
# Report browser
# ---------------------------------------------------------------------------

DIR_STYLE = """\
body { font-family: -apple-system, sans-serif; max-width: 800px;
       margin: 40px auto; padding: 0 20px; color: #1a1a1a; }
h1 { font-size: 1.4em; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }
a { color: #2563eb; text-decoration: none; }
a:hover { text-decoration: underline; }
ul { list-style: none; padding: 0; }
li { padding: 6px 0; border-bottom: 1px solid #f1f5f9; }
li::before { content: "📁 "; }
li.file::before { content: "📄 "; }
"""


@app.get("/reports/{path:path}", response_class=HTMLResponse)
async def browse_reports(path: str = ""):
    """Browse reports directory or serve files."""
    target = (REPORTS_DIR / path).resolve()

    if not str(target).startswith(str(REPORTS_DIR)):
        raise HTTPException(status_code=403, detail="Forbidden")

    if not target.exists():
        raise HTTPException(status_code=404, detail="Not found")

    if target.is_file():
        return FileResponse(target)

    rel = target.relative_to(REPORTS_DIR)
    title = f"/{rel}" if str(rel) != "." else "/"

    items: list[str] = []
    if str(rel) != ".":
        parent = f"/reports/{rel.parent}" if str(rel.parent) != "." else "/reports/"
        items.append(f'<li><a href="{parent}">..</a></li>')

    for entry in sorted(target.iterdir()):
        name = entry.name
        href = f"/reports/{rel / name}" if str(rel) != "." else f"/reports/{name}"
        css_class = "" if entry.is_dir() else ' class="file"'
        display = f"{name}/" if entry.is_dir() else name
        items.append(f'<li{css_class}><a href="{href}">{display}</a></li>')

    list_html = "\n".join(items) if items else "<p>Empty directory.</p>"
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Reports {title}</title>
<style>{DIR_STYLE}</style></head>
<body><h1>Reports {title}</h1><ul>{list_html}</ul></body></html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    """Redirect to reports browser."""
    return HTMLResponse(
        status_code=307,
        headers={"Location": "/reports/"},
    )


# ---------------------------------------------------------------------------
# Audit status endpoint
# ---------------------------------------------------------------------------

@app.get("/audit-status/{path:path}")
async def audit_status(path: str):
    """Check if an audit report is ready.

    Returns {"status": "completed", "report_url": ...} or {"status": "pending"}.
    """
    report_path = REPORTS_DIR / path
    if not str(report_path.resolve()).startswith(str(REPORTS_DIR)):
        raise HTTPException(status_code=403, detail="Forbidden")

    if report_path.exists() and report_path.is_file():
        return {"status": "completed", "report_url": f"/reports/{path}"}
    return {"status": "pending"}


# ---------------------------------------------------------------------------
# Audit endpoints (async — return immediately, audit runs in background)
# ---------------------------------------------------------------------------

@app.post("/audit-security/{skill}", dependencies=[Depends(verify_api_key)])
async def audit(skill: str, file: UploadFile = File(...)):
    logger.info("Received audit request: file=%s, skill=%s", file.filename, skill)

    # 1. Validate file type
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a .zip archive")

    # 2. Validate skill
    skills = _cached_skills()
    if skill not in skills:
        available = list(skills.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Skill '{skill}' not found. Available skills: {available}",
        )

    # 3. Create report directory
    project_name = _sanitize_name(file.filename.removesuffix(".zip"))
    if not project_name:
        project_name = "unnamed"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    report_dir = REPORTS_DIR / project_name / "security" / timestamp
    report_dir.mkdir(parents=True, exist_ok=True)
    code_dir = report_dir / "code"
    code_dir.mkdir(exist_ok=True)

    # 4. Read, validate, and extract zip (synchronous — fast)
    content = await file.read()
    _validate_and_extract_zip(content, report_dir, code_dir)

    # 5. Submit audit to background thread pool and return immediately
    report_url = (
        f"/reports/{project_name}/security/{timestamp}/audit-report.html"
    )
    status_path = f"{project_name}/security/{timestamp}/audit-report.html"
    skill_obj = skills[skill]

    _executor.submit(
        _run_security_audit_background,
        skill=skill_obj,
        code_dir=code_dir,
        report_dir=report_dir,
        report_url=report_url,
    )

    return {
        "report_url": report_url,
        "status_url": f"/audit-status/{status_path}",
        "status": "processing",
    }


@app.post("/audit-pr/{skill}", dependencies=[Depends(verify_api_key)])
async def audit_pr(
    skill: str,
    file: UploadFile = File(...),
    from_branch: str = Form(...),
    to_branch: str = Form(...),
):
    logger.info(
        "Received PR audit request: file=%s, skill=%s, from=%s, to=%s",
        file.filename,
        skill,
        from_branch,
        to_branch,
    )

    # 1. Validate file type
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a .zip archive")

    # 2. Validate skill
    skills = _cached_skills()
    if skill not in skills:
        available = list(skills.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Skill '{skill}' not found. Available skills: {available}",
        )

    # 3. Validate branch params
    if not from_branch.strip():
        raise HTTPException(status_code=400, detail="from_branch must not be empty")
    if not to_branch.strip():
        raise HTTPException(status_code=400, detail="to_branch must not be empty")

    # 4. Create report directory
    project_name = _sanitize_name(file.filename.removesuffix(".zip"))
    if not project_name:
        project_name = "unnamed"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    report_dir = REPORTS_DIR / project_name / "pr" / timestamp
    report_dir.mkdir(parents=True, exist_ok=True)
    code_dir = report_dir / "code"
    code_dir.mkdir(exist_ok=True)

    # 5. Read, validate, and extract zip
    content = await file.read()
    _validate_and_extract_zip(content, report_dir, code_dir)

    # 6. Verify git repository
    git_dir = code_dir / ".git"
    if not git_dir.exists():
        subdirs = [d for d in code_dir.iterdir() if d.is_dir()]
        nested_git = next(
            (d / ".git" for d in subdirs if (d / ".git").exists()),
            None,
        )
        if nested_git is None:
            shutil.rmtree(report_dir, ignore_errors=True)
            raise HTTPException(
                status_code=400,
                detail=(
                    "Zip must contain a git repository (.git directory) "
                    "for PR audit. Do not exclude .git when packaging."
                ),
            )

    # 7. Submit audit to background thread pool and return immediately
    report_url = f"/reports/{project_name}/pr/{timestamp}/audit-report.html"
    status_path = f"{project_name}/pr/{timestamp}/audit-report.html"
    skill_obj = skills[skill]

    _executor.submit(
        _run_pr_audit_background,
        skill=skill_obj,
        code_dir=code_dir,
        report_dir=report_dir,
        report_url=report_url,
        from_branch=from_branch.strip(),
        to_branch=to_branch.strip(),
    )

    return {
        "report_url": report_url,
        "status_url": f"/audit-status/{status_path}",
        "status": "processing",
    }
