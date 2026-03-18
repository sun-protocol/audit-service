from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    claude_code_token: str = ""
    api_keys: str = ""  # comma-separated list of valid API keys for audit service
    skills_dir: str = "./skills"
    claude_model: str = "claude-sonnet-4-6"
    max_upload_size: int = 52_428_800  # 50MB

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def get_api_keys(self) -> set[str]:
        if not self.api_keys:
            return set()
        return {k.strip() for k in self.api_keys.split(",") if k.strip()}


settings = Settings()
