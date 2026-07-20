from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Cryptanium"
    API_VERSION: str = "v1"

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    DATABASE_URL: str = ""

    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    OPENROUTER_API_KEY: str = ""

    SECRET_KEY: str = "change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()