import os
import re
from pathlib import Path
from typing import Literal, Self

import ryaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..output import OutputType

DEFAULT_HOME_DIRECTORY = Path.home() / ".sigye"
DEFAULT_HOME_DIRECTORY.mkdir(exist_ok=True, parents=True)
DEFAULT_CONFIG_PATH = DEFAULT_HOME_DIRECTORY / "config.yaml"
DEFAULT_DATA_FILENAME = DEFAULT_HOME_DIRECTORY / "time_entries.toml"
DEFAULT_EDITOR = os.getenv("EDITOR", "nano")


class AutoTagRule(BaseModel):
    pattern: str
    match_type: Literal["regex"]  # Using regex for all pattern matching
    tags: list[str]


class Settings(BaseSettings):
    data_filename: str = Field(default=str(DEFAULT_DATA_FILENAME))
    locale: str = Field(default="en_US")
    auto_tag_rules: list[AutoTagRule] = []
    editor: str = Field(default=DEFAULT_EDITOR)  # really the editor command in the shell
    editor_format: str = Field(default="yaml")  # the format of the editor file
    output_format: OutputType = Field(default=OutputType.EMPTY)

    @classmethod
    def load_from_file(cls, path: Path = DEFAULT_CONFIG_PATH) -> Self:
        if not path.exists():
            return cls()
        with open(path) as f:
            config_dict = ryaml.load(f)
            return cls.model_validate(config_dict or {})

    def apply_auto_tags(self, project: str) -> set[str]:
        """Apply auto-tagging rules to a project name and return the set of tags to add"""
        tags = set()
        for rule in self.auto_tag_rules:
            if re.search(rule.pattern, project):
                tags.update(rule.tags)
        return tags

    model_config = SettingsConfigDict(env_prefix="sigye_", extra="ignore")
