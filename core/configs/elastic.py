from pydantic.fields import Field
from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict


class ElasticSettings(BaseSettings):
    """
    This class is used to store the Postgres connection settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # user: str = Field(default=..., alias="ELASTIC_SCHEME")
    host: str = Field(default=..., alias="ELASTIC_HOST")
    port: int = Field(default=9200, alias="ELASTIC_PORT")

    buffer_size: int = Field(100, env="ELASTIC_MIGRATE_BUFFERED_ROWS")
    sleep_time: float = Field(60.0, env="ELASTIC_MIGRATE_SLEEP_TIME")

    @property
    def get_dsn(self):
        return f"http://{self.host}:{self.port}"


settings = ElasticSettings()
