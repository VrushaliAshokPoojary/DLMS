from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str = "dlms"
    postgres_password: str = "dlms"
    postgres_db: str = "dlms"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "dlms"

    @property
    def postgres_dsn(self) -> str:
        return (
            "postgresql+psycopg2://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
