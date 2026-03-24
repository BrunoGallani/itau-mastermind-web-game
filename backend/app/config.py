from datetime import datetime, timezone
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


def utc_now() -> datetime:
    """Retorna datetime UTC naive (compatível com SQLite) sem usar utcnow() depreciado."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "mastermind.db"

class Settings(BaseSettings):
    database_url: str = f"sqlite:///{DB_PATH.as_posix()}"

    # Sessao
    session_duration_hours: int = 24

    # Cookie
    cookie_httponly: bool = True
    cookie_samesite: str = "lax"

    # CORS
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # FastAPI
    app_title: str = "Mastermind API"
    app_description: str = "API REST para o jogo Mastermind"
    app_version: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
