from psycopg2.extras import DictCursor
from pydantic import SecretStr
from pydantic.fields import Field
from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    """
    This class is used to store the Postgres connection settings.
    """

    db_name: str = Field(default=..., alias="POSTGRES_DB")
    user: str = Field(default=..., alias="POSTGRES_USER")
    password: SecretStr = Field(default=..., alias="POSTGRES_PASSWORD")
    host: str = Field(default=..., alias="POSTGRES_HOST")
    port: int = Field(default=..., alias="POSTGRES_PORT")

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
