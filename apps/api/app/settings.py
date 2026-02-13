from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")

    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_issuer: str = Field(alias="JWT_ISSUER")
    access_token_minutes: int = Field(default=30, alias="ACCESS_TOKEN_MINUTES")

    encryption_master_key: str = Field(alias="ENCRYPTION_MASTER_KEY")

    stripe_secret_key: str = Field(alias="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(alias="STRIPE_WEBHOOK_SECRET")

settings = Settings()
