from pydantic_settings import BaseSettings
from pydantic import Field


class BaseAppSettings(BaseSettings):
    # Shared defaults
    KAFKA_BOOTSTRAP_SERVERS: str = Field("kafka:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    REDIS_HOST: str = Field("redis", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class FinnhubSettings(BaseAppSettings):
    FINNHUB_API_KEY: str = Field(..., env="FINNHUB_API_KEY")


class PolygonFlatfileSettings(BaseAppSettings):
    POLYGON_ACCESS_KEY_ID: str = Field(..., env="POLYGON_ACCESS_KEY_ID")
    POLYGON_SECRET_ACCESS_KEY: str = Field(..., env="POLYGON_SECRET_ACCESS_KEY")
    POLYGON_S3_ENDPOINT: str = Field("https://files.polygon.io", env="POLYGON_S3_ENDPOINT")
    POLYGON_BUCKET_NAME: str = Field("flatfiles", env="POLYGON_BUCKET_NAME")


class PolygonStocksSettings(BaseAppSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    POLYGON_API_KEY: str = Field(..., env="POLYGON_API_KEY")
    FINNHUB_API_KEY: str = Field(..., env="FINNHUB_API_KEY")

    # KAFKA_BROKER alias to KAFKA_BOOTSTRAP_SERVERS
    @property
    def KAFKA_BROKER(self):
        return self.KAFKA_BOOTSTRAP_SERVERS




