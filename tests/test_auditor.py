from pathlib import Path
from unittest.mock import patch

import pytest

from src.audit_service.auditor import run_audit
from src.audit_service.skill_loader import Skill


def _make_skill(**kwargs) -> Skill:
    defaults = {
        "name": "test",
        "description": "test skill",
        "prompt": "You are an auditor.",
        "skill_dir": Path("/tmp/skills/test"),
    }
    defaults.update(kwargs)
    return Skill(**defaults)


@pytest.mark.asyncio
async def test_run_audit_returns_markdown():
    class MockResult:
        result = "# Audit Report\n\nNo issues found."

    async def mock_query(*args, **kwargs):
        yield MockResult()

    with (
        patch("src.audit_service.auditor.query", side_effect=mock_query),
        patch("src.audit_service.auditor.ResultMessage", MockResult),
        patch("src.audit_service.auditor.resolve_auth_env", return_value={}),
    ):
        result = await run_audit(
            skill=_make_skill(),
            code_dir="/tmp/test-code",
        )

    assert "Audit Report" in result


@pytest.mark.asyncio
async def test_run_audit_concatenates_multiple_results():
    class MockResult:
        def __init__(self, text):
            self.result = text

    results = [MockResult("# Part 1"), MockResult("## Part 2")]

    async def mock_query(*args, **kwargs):
        for r in results:
            yield r

    with (
        patch("src.audit_service.auditor.query", side_effect=mock_query),
        patch("src.audit_service.auditor.ResultMessage", type(results[0])),
        patch("src.audit_service.auditor.resolve_auth_env", return_value={}),
    ):
        result = await run_audit(
            skill=_make_skill(),
            code_dir="/tmp/code",
        )

    assert "Part 1" in result
    assert "Part 2" in result


@pytest.mark.asyncio
async def test_run_audit_passes_skill_dir_as_add_dirs():
    class MockResult:
        result = "# Report"

    captured_options = {}

    async def mock_query(*args, **kwargs):
        captured_options.update(kwargs)
        yield MockResult()

    skill = _make_skill(skill_dir=Path("/my/skills/security-audit"))

    with (
        patch("src.audit_service.auditor.query", side_effect=mock_query),
        patch("src.audit_service.auditor.ResultMessage", MockResult),
        patch("src.audit_service.auditor.resolve_auth_env", return_value={}),
    ):
        await run_audit(skill=skill, code_dir="/tmp/code")

    options = captured_options["options"]
    assert "/my/skills/security-audit" in options.add_dirs
