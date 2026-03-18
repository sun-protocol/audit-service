import asyncio
import logging
import re
import shutil
import zipfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import APIKeyHeader

from .auditor import run_audit
from .config import settings
from .html_converter import markdown_to_html
from .skill_loader import load_skills

logger = logging.getLogger(__name__)

REPORTS_DIR = Path("reports").resolve()
REPORTS_DIR.mkdir(exist_ok=True)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@lru_cache
def _cached_skills():
    return load_skills(settings.skills_dir)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    _cached_skills()
    logger.info("Loaded skills: %s", list(_cached_skills().keys()))
    yield


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


@app.post("/audit/{skill}", dependencies=[Depends(verify_api_key)])
async def audit(skill: str, file: UploadFile = File(...)):
    logger.info("Received audit request: file=%s, skill=%s", file.filename, skill)

    # 1. Validate file type first (cheap check)
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

    # 3. Create report directory: reports/<project_name>/<timestamp>/
    project_name = _sanitize_name(file.filename.removesuffix(".zip"))
    if not project_name:
        project_name = "unnamed"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    report_dir = REPORTS_DIR / project_name / timestamp
    report_dir.mkdir(parents=True, exist_ok=True)

    code_dir = report_dir / "code"
    code_dir.mkdir(exist_ok=True)

    try:
        content = await file.read()

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

        # 4. Run audit
        skill_obj = skills[skill]
        agent_output = await run_audit(
            skill=skill_obj,
            code_dir=str(code_dir),
        )
        await asyncio.sleep(2)

        # 5. Read report from skill-defined path, fallback to agent output
        report_candidates = [
            code_dir / skill_obj.report_path,
            report_dir / skill_obj.report_path,
        ]
        skill_report_file = next(
            (f for f in report_candidates if f.exists()), None
        )
        if skill_report_file is not None:
            md_report = skill_report_file.read_text(encoding="utf-8")
            logger.info("Using report from %s", skill_report_file)
        else:
            md_report = agent_output
            logger.info(
                "Report file %s not found, using agent output",
                skill_obj.report_path,
            )

        # 6. Convert to HTML and save
        html_content = markdown_to_html(md_report, title=f"Audit Report - {skill}")
        html_path = report_dir / "audit-report.html"
        html_path.write_text(html_content, encoding="utf-8")

        report_url = f"/reports/{project_name}/{timestamp}/audit-report.html"
        logger.info("Audit report saved to %s", report_dir)

        # 7. Return report URL
        return {"report_url": report_url}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Audit failed: skill=%s file=%s", skill, file.filename)
        raise HTTPException(
            status_code=500, detail="Audit failed. See server logs."
        )
    finally:
        # Clean up report_dir on failure (no audit-report.html means incomplete)
        if not (report_dir / "audit-report.html").exists():
            shutil.rmtree(report_dir, ignore_errors=True)
