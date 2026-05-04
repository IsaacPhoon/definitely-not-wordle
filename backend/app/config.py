from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://localhost:5432/wordle"
    secret_key: str | None = None
    allowed_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env"}

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        # Heroku commonly provides DATABASE_URL as `postgres://...` (or `postgresql://...`).
        # SQLAlchemy async URLs should be `postgresql+asyncpg://...`.
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace(
                "postgres://", "postgresql+asyncpg://", 1
            )
        elif self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )

        if self.environment.lower() != "development" and not self.secret_key:
            raise ValueError("SECRET_KEY is required in non-development environments")


settings = Settings()
