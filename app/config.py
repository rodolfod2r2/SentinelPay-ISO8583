"""Configuração da aplicação."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente."""

    # API
    app_name: str = "Motor de Autorização de Benefícios Flexíveis"
    debug: bool = False

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/beneficios_flex"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    velocity_window_seconds: int = 300  # 5 min para velocity check

    # ISO 8583
    default_currency_code: str = "986"  # BRL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
