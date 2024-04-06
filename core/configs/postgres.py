from psycopg2.extras import DictCursor
from pydantic import SecretStr
from pydantic.fields import Field
from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict


class PostgresSettings(BaseSettings):
    """
    This class is used to store the Postgres connection settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    db_name: str = Field(default=..., alias="POSTGRES_DB")
    user: str = Field(default=..., alias="POSTGRES_USER")
    password: SecretStr = Field(default=..., alias="POSTGRES_PASSWORD")
    host: str = Field(default=..., alias="POSTGRES_HOST")
    port: int = Field(default=..., alias="POSTGRES_PORT")

    @property
    def psycopg2_connect_local(self) -> dict:
        return {
            "dbname": self.db_name,
            "user": self.user,
            "password": self.password.get_secret_value(),
            "host": "127.0.0.1",
            "port": self.port,
            "cursor_factory": DictCursor,
        }

    @property
    def psycopg2_connect(self) -> dict:
        return {
            "dbname": self.db_name,
            "user": self.user,
            "password": self.password.get_secret_value(),
            "host": self.host,
            "port": self.port,
            "cursor_factory": DictCursor,
        }


settings = PostgresSettings()
