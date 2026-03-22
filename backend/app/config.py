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
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
