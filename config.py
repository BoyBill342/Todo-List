from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db: str = "sqlite+aiosqlite:///./todos.db"
settings = Settings ()