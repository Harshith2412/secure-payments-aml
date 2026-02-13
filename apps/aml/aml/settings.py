from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    aml_alert_threshold: int = Field(default=70, alias="AML_ALERT_THRESHOLD")
    high_risk_countries: str = Field(default="IR,KP,SY,CU,RU", alias="HIGH_RISK_COUNTRIES")

settings = Settings()
