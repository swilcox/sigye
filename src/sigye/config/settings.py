from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_HOME_DIRECTORY = Path.home() / ".sigye"
DEFAULT_HOME_DIRECTORY.mkdir(exist_ok=True, parents=True)


class Settings(BaseSettings):
    data_filename: str = Field(default=str(DEFAULT_HOME_DIRECTORY / "time_entries.yml"))
    locale: str = Field(default="en_US")
    model_config = SettingsConfigDict(env_prefix="sigye_")
