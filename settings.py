from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    max_pages: int = 5
    proxy: str = ""
    auth_token: str = "secret-token"

settings = Settings()
