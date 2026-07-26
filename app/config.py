from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "shopnorv@gmail.com"
    SMTP_PASSWORD: str = "rgrnncbprxswdzai"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
