import io
import zipfile
from pathlib import Path
from unittest.mock import patch

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


@pytest.fixture
def test_zip() -> bytes:
    return _make_zip({"main.py": "print('hello')"})


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
async def test_audit_rejected_without_api_key(test_zip: bytes):
    with patch("src.audit_service.main.settings") as mock_settings:
        mock_settings.get_api_keys.return_value = {"ask-valid-key"}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/audit-security/backend-server-scanner",
                files={"file": ("code.zip", test_zip, "application/zip")},
            )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_audit_rejected_with_wrong_api_key(test_zip: bytes):
    with patch("src.audit_service.main.settings") as mock_settings:
        mock_settings.get_api_keys.return_value = {"ask-valid-key"}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/audit-security/backend-server-scanner",
                files={"file": ("code.zip", test_zip, "application/zip")},
                headers={"X-API-Key": "ask-wrong-key"},
            )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_audit_invalid_skill(test_zip: bytes):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/audit-security/nonexistent-skill",
            files={"file": ("code.zip", test_zip, "application/zip")},
        )
    assert resp.status_code == 400
    assert "not found" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_audit_non_zip_filename():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/audit-security/backend-server-scanner",
            files={"file": ("code.tar.gz", b"data", "application/gzip")},
        )
    assert resp.status_code == 400
    assert "zip" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_audit_invalid_zip(test_zip: bytes):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/audit-security/backend-server-scanner",
            files={"file": ("code.zip", b"not a zip", "application/zip")},
        )
    assert resp.status_code == 400
    assert "invalid zip" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_audit_success(test_zip: bytes):
    """Endpoint should return immediately with processing status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("src.audit_service.main._executor") as mock_executor:
            resp = await client.post(
                "/audit-security/backend-server-scanner",
                files={"file": ("code.zip", test_zip, "application/zip")},
            )
            mock_executor.submit.assert_called_once()

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "processing"
    assert data["report_url"].endswith("/audit-report.html")
    assert "/security/" in data["report_url"]
    assert "status_url" in data


@pytest.mark.asyncio
async def test_audit_sanitizes_project_name():
    malicious_zip = _make_zip({"main.py": "x"})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("src.audit_service.main._executor"):
            resp = await client.post(
                "/audit-security/backend-server-scanner",
                files={
                    "file": ("../../etc/passwd.zip", malicious_zip, "application/zip")
                },
            )

    assert resp.status_code == 200
    url = resp.json()["report_url"]
    assert ".." not in url
    assert "/etc/" not in url
