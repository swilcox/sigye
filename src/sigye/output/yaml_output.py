from pathlib import Path

import ryaml

from ..models import TimeEntry
from .output import OutputFormatter


class YamlOutput(OutputFormatter):
    def single_entry_output(self, entry: TimeEntry | None) -> None:
        if entry is None:
            return
        print(ryaml.dumps(entry.model_dump(mode="json")))

    def multiple_entries_output(self, entries: list[TimeEntry]) -> None:
        print(ryaml.dumps({"entries": [entry.model_dump(mode="json") for entry in entries]}))

    def export_output(self, count: int, filename: Path | str) -> None:
        print("")
