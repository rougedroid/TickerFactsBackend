from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    HOST: str
    PORT: int

    DEBUG: bool

    SECRET_KEY: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    GOOGLE_CLIENT_ID: str
    PIPELINE_API_KEY: str
    SEC_USER_AGENT: str
    INTERNAL_API_KEY: str
    API_URL: str
    REDIS_URL: str
    FINNHUB_API_KEY: str
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
