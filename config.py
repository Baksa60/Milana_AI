from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "google/gemma-2-9b-it:free"
    ADMIN_IDS: List[int] = Field(default_factory=list)
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
