from unittest.mock import patch

from src.audit_service.auth import resolve_auth_env


def test_resolve_auth_env_api_key():
    with patch("src.audit_service.auth.settings") as mock:
        mock.anthropic_api_key = "sk-ant-test"
        mock.claude_code_oauth_token = ""
        env = resolve_auth_env()
    assert env == {"ANTHROPIC_API_KEY": "sk-ant-test"}


def test_resolve_auth_env_claude_code_oauth_token():
    with patch("src.audit_service.auth.settings") as mock:
        mock.anthropic_api_key = ""
        mock.claude_code_oauth_token = "cct-test-token"
        env = resolve_auth_env()
    assert env == {"CLAUDE_CODE_OAUTH_TOKEN": "cct-test-token"}


def test_resolve_auth_env_api_key_takes_precedence():
    with patch("src.audit_service.auth.settings") as mock:
        mock.anthropic_api_key = "sk-ant-test"
        mock.claude_code_oauth_token = "cct-test-token"
        env = resolve_auth_env()
    assert env == {"ANTHROPIC_API_KEY": "sk-ant-test"}


def test_resolve_auth_env_empty():
    with patch("src.audit_service.auth.settings") as mock:
        mock.anthropic_api_key = ""
        mock.claude_code_oauth_token = ""
        env = resolve_auth_env()
    assert env == {}
