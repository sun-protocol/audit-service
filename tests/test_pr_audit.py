import io
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.audit_service.main import app
from src.audit_service.skill_loader import Skill

FAKE_SKILL = Skill(
    name="backend-server-scanner",
    description="test",
    prompt="You are an auditor.",
    skill_dir=Path("./skills/backend-server-scanner"),
)
FAKE_SKILLS = {"backend-server-scanner": FAKE_SKILL}


def _make_zip(files: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _make_git_zip() -> bytes:
    """Create a zip with a .git directory so it passes the git check."""
    return _make_zip({
        "main.py": "print('hello')",
        ".git/HEAD": "ref: refs/heads/main\n",
    })


@pytest.fixture
def test_zip() -> bytes:
    return _make_zip({"main.py": "print('hello')"})


@pytest.fixture
def git_zip() -> bytes:
    return _make_git_zip()


@pytest.fixture(autouse=True)
def _mock_skills():
    with patch("src.audit_service.main._cached_skills", return_value=FAKE_SKILLS):
        yield


@pytest.fixture(autouse=True)
def _disable_api_key_auth():
    with patch("src.audit_service.main.settings") as mock_settings:
        mock_settings.get_api_keys.return_value = set()
        mock_settings.max_upload_size = 52_428_800
        yield mock_settings


@pytest.mark.asyncio
async def test_pr_audit_missing_from_branch(test_zip: bytes):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/audit-pr/backend-server-scanner",
            files={"file": ("code.zip", test_zip, "application/zip")},
            data={"to_branch": "feature/xxx"},
        )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_pr_audit_missing_to_branch(test_zip: bytes):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/audit-pr/backend-server-scanner",
            files={"file": ("code.zip", test_zip, "application/zip")},
            data={"from_branch": "main"},
        )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_pr_audit_non_zip_file():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/audit-pr/backend-server-scanner",
            files={"file": ("code.tar.gz", b"data", "application/gzip")},
            data={"from_branch": "main", "to_branch": "feature/xxx"},
        )
    assert resp.status_code == 400
    assert "zip" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_pr_audit_invalid_skill(test_zip: bytes):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/audit-pr/nonexistent-skill",
            files={"file": ("code.zip", test_zip, "application/zip")},
            data={"from_branch": "main", "to_branch": "feature/xxx"},
        )
    assert resp.status_code == 400
    assert "not found" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_pr_audit_missing_git_directory(test_zip: bytes):
    """Zip without .git directory should be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/audit-pr/backend-server-scanner",
            files={"file": ("code.zip", test_zip, "application/zip")},
            data={"from_branch": "main", "to_branch": "feature/xxx"},
        )
    assert resp.status_code == 400
    assert ".git" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_pr_audit_success(git_zip: bytes):
    mock_result = AsyncMock()
    mock_result.result = "# PR Audit Report\n\nNo issues."

    async def mock_query(*args, **kwargs):
        yield mock_result

    with (
        patch("src.audit_service.auditor.query", side_effect=mock_query),
        patch("src.audit_service.auditor.ResultMessage", type(mock_result)),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/audit-pr/backend-server-scanner",
                files={"file": ("code.zip", git_zip, "application/zip")},
                data={"from_branch": "main", "to_branch": "feature/new-token"},
            )

    assert resp.status_code == 200
    assert "report_url" in resp.json()
    assert "/pr/" in resp.json()["report_url"]
    assert resp.json()["report_url"].endswith("/audit-report.html")
