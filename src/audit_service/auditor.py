from claude_code_sdk import ClaudeCodeOptions, ResultMessage, query

from .auth import resolve_auth_env
from .config import settings
from .skill_loader import Skill, build_system_prompt


async def run_audit(skill: Skill, code_dir: str) -> str:
    """Run a code audit using Claude Code SDK.

    Returns the Markdown audit report.
    """
    system_prompt = build_system_prompt(skill)
    result_parts: list[str] = []

    async for message in query(
        prompt=(
            f"Audit all code in the {code_dir} directory and generate a complete audit report in Markdown format. "
            "The report should include: an overview, detailed findings, severity classifications, remediation recommendations, and a summary."
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
        if isinstance(message, ResultMessage):
            result_parts.append(message.result)

    return "\n".join(result_parts)
