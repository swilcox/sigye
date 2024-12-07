import yaml

from ..models import TimeEntry
from .output import OutputFormatter


class YamlOutput(OutputFormatter):
    def single_entry_output(self, entry: TimeEntry | None) -> None:
        if entry is None:
            return
        print(yaml.dump(entry.model_dump(mode="json")))

    def multiple_entries_output(self, entries: list[TimeEntry]) -> None:
        print(yaml.dump({"entries": [entry.model_dump(mode="json") for entry in entries]}))
