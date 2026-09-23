from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_host: str = "db"
    db_port: int = 3306
    db_name: str = "haaletus"
    db_user: str = "haaletus"
    db_password: str = "haaletus"

    # Üks hääletus kestab 5 minutit
    vote_duration_seconds: int = 300

    cors_origins: str = "*"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
