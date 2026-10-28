from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env")
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    database_url: str
    milvus_uri: str = "http://localhost:19530"
    jwt_secret: str
    jwt_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:return Settings()