from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = "sqlite:///./test.db"

    # Auth / JWT
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email (por si luego los usas)
    EMAIL_HOST: str = "smtp.example.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = "your_email@example.com"
    EMAIL_PASSWORD: str = "your_email_password"
    EMAIL_FROM: str = "your_email@example.com"

    # Debug
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
