from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Pokedex API"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/pokedex"
    POKEAPI_BASE: str = "https://pokeapi.co/api/v2"
    MAX_CONCURRENT_REQUESTS: int = 8
    HTTP_TIMEOUT_SECONDS: float = 20.0

    DEFAULT_LIMIT: int = 20
    MAX_LIMIT: int = 200

    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:4200",
            "http://localhost:5173",
        ]
    )

settings = Settings()