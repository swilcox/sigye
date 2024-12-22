from enum import StrEnum
from pathlib import Path

from ..models import TimeEntry


class OutputType(StrEnum):
    TEXT = "text"
    JSON = "json"
    RICH = "rich"
    YAML = "yaml"
    MARKDOWN = "markdown"
    EMPTY = ""

    @classmethod
    def choices(cls) -> list[str]:
        return [x.value for x in cls]


class OutputFormatter:
    """The Base OutputFormatter class that all output classes should inherit from."""

    def __init__(self):
        pass

    def single_entry_output(self, entry: TimeEntry) -> None:
        raise NotImplementedError("output method is not implemented")

    def multiple_entries_output(self, entries: list[TimeEntry]) -> None:
        raise NotImplementedError("output method is not implemented")

    def export_output(self, count: int, filename: Path | str) -> None:
        raise NotImplementedError("output method is not implemented")
