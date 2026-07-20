from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Cryptanium"
    API_VERSION: str = "v1"

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    DATABASE_URL: str = "sqlite:///./cryptanium.db"

    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://127.0.0.1:8000/auth/callback"

    OPENROUTER_API_KEY: str = ""

    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
