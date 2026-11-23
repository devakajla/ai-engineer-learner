from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, read from environment variables (and a local .env file)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "TaskFlow"
    version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = "/api/v1"


settings = Settings()
