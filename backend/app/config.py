from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

class Settings(BaseSettings):
    database_url: str = f"sqlite:///{DATA_DIR / 'mastermind.db'}"
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
