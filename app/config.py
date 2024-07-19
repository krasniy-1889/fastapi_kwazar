from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    db_path: str = "kwazar.sqlite3"

    @property
    def DB_URL(self) -> str:
        return f"sqlite+aiosqlite:///./{self.db_path}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Config()  # type: ignore
