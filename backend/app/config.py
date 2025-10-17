from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    database_url: str = "postgresql+asyncpg://soc_user:soc_password@postgres:5432/soc"
    uvicorn_host: str = "0.0.0.0"
    uvicorn_port: int = 8000
    cors_allowed_origins: list[str] = ["*"]
    default_scan_targets: str = "192.168.1.0/24"


settings = Settings()
