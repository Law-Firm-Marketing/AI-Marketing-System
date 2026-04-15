from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'AI Marketing Orchestration System'
    debug: bool = False

    postgres_url: str = 'postgresql+psycopg2://marketing:marketing@postgres:5432/marketing'
    redis_url: str = 'redis://redis:6379/0'

    workflow_max_retries: int = 2


settings = Settings()
