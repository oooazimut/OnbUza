from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModBusSettings(BaseModel):
    host: str
    port: int


class Settings(BaseSettings):
    bot_token: SecretStr
    db_name: str
    passwd: SecretStr
    modbus: ModBusSettings
    common_img: str
    archive_img: str

    @property
    def sqlite_async_dsn(self):
        return f"sqlite+aiosqlite:///{self.db_name}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


PUMPS = ["ДТ-1", "ДТ-2", "АИ-9х.1", "АИ-9х.2", "РЕЗ"]

settings = Settings()
