import logging

import claude_code_sdk._internal.client as _client
import claude_code_sdk._internal.message_parser as _mp
from claude_code_sdk import ClaudeCodeOptions, ResultMessage, query

from .auth import resolve_auth_env
from .config import settings
from .skill_loader import Skill, build_system_prompt

logger = logging.getLogger(__name__)

# Workaround: claude-code-sdk<=0.0.25 does not handle `rate_limit_event` messages
# from the API, causing MessageParseError. This patch skips unknown message types
# so audits can complete normally. Remove once the SDK adds native support.
_original_parse = _mp.parse_message


def _patched_parse(data):
    try:
        return _original_parse(data)
    except _mp.MessageParseError as e:
        if "Unknown message type" in str(e):
            logger.debug("Skipping unknown SDK message: %s", e)
            return None
        raise


_mp.parse_message = _patched_parse
_client.parse_message = _patched_parse


async def run_audit(skill: Skill, code_dir: str) -> str:
    """Run a code audit using Claude Code SDK.

    Returns the Markdown audit report.
    """
    system_prompt = build_system_prompt(skill)
    result_parts: list[str] = []

    async for message in query(
        prompt=(
            f"Audit all code in the {code_dir} directory and generate "
            "a complete audit report in Markdown format. "
            "The report should include: an overview, detailed findings, "
            "severity classifications, remediation recommendations, "
            "and a summary."
        ),
        options=ClaudeCodeOptions(
            cwd=code_dir,
            allowed_tools=["Read", "Glob", "Grep"],
            system_prompt=system_prompt,
            permission_mode="bypassPermissions",
            model=settings.claude_model,
            add_dirs=[str(skill.skill_dir)],
            env=resolve_auth_env(),
        ),
    ):
        if message is not None and isinstance(message, ResultMessage):
            result_parts.append(message.result)

    return "\n".join(result_parts)


async def run_pr_audit(
    skill: Skill,
    code_dir: str,
    from_branch: str,
    to_branch: str,
) -> str:
    """Run a PR-focused audit using Claude Code SDK.

    Diffs from_branch...to_branch and audits the changed code.
    Returns the Markdown audit report.
    """
    system_prompt = build_system_prompt(skill)
    result_parts: list[str] = []

    async for message in query(
        prompt=(
            f"You are auditing a PR from '{from_branch}' to '{to_branch}'. "
            f"First run `git diff {from_branch}...{to_branch}` in {code_dir} "
            "to see the changes. "
            "ONLY audit the code changed between from_branch and to_branch. "
            "Do NOT audit unchanged code. "
            "Generate a complete Markdown audit report including: "
            "PR change overview, detailed findings on the diff, "
            "severity classifications, remediation recommendations, "
            "and a summary."
        ),
        options=ClaudeCodeOptions(
            cwd=code_dir,
            allowed_tools=["Read", "Glob", "Grep", "Bash"],
            system_prompt=system_prompt,
            permission_mode="bypassPermissions",
            model=settings.claude_model,
            add_dirs=[str(skill.skill_dir)],
            env=resolve_auth_env(),
        ),
    ):
        if message is not None and isinstance(message, ResultMessage):
            result_parts.append(message.result)

    return "\n".join(result_parts)
