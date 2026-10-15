from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Central application configuration loaded from environment variables.
    Fails startup immediately if required values are missing or invalid.
    """


    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    PROJECT_NAME: str = "Career Copilot"
    DEBUG: bool = False

    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    SECRET_KEY: str = Field(..., min_length=16)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GEMINI_API_KEY:str
    ADZUNA_APP_ID:str
    ADZUNA_APP_KEY:str
    REDIS_URL:str
    

@lru_cache()
def get_settings() -> Settings:
    """Returns a singleton instance of the validated application settings."""
    return Settings() # type: ignore

if __name__ == "__main__":
    settings = get_settings()
    print(f"Project Name: {settings.PROJECT_NAME}")
    print(f"Debug Mode: {settings.DEBUG}")