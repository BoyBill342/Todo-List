from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str ="API_SECRET_KEY_TEST"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int= 30
    db: str = "sqlite+aiosqlite:///./todos.db"
settings = Settings ()