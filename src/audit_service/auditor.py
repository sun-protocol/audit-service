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
            f"请审计 {code_dir} 目录下的所有代码，按照审计规则生成完整的审计报告（Markdown格式）。"
            "报告应包含：概述、详细发现、严重程度分类、修复建议和总结。"
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
