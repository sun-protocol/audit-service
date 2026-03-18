import logging

from .config import settings

logger = logging.getLogger(__name__)


def resolve_auth_env() -> dict[str, str]:
    """Resolve authentication environment variables for Claude Code SDK.

    Returns env dict with the appropriate auth token:
    - ANTHROPIC_API_KEY mode: uses Anthropic API key directly
    - CLAUDE_CODE_TOKEN mode: uses Claude Code subscription token
    - Both empty: returns empty dict, logs a warning
    """
    if settings.anthropic_api_key:
        return {"ANTHROPIC_API_KEY": settings.anthropic_api_key}
    if settings.claude_code_token:
        return {"CLAUDE_CODE_TOKEN": settings.claude_code_token}
    logger.warning(
        "No ANTHROPIC_API_KEY or CLAUDE_CODE_TOKEN configured. "
        "Claude Code SDK authentication may fail."
    )
    return {}
