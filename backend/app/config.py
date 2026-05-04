from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://localhost:5432/wordle"
    secret_key: str | None = None
    allowed_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env"}

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        if self.environment.lower() != "development" and not self.secret_key:
            raise ValueError("SECRET_KEY is required in non-development environments")


settings = Settings()
