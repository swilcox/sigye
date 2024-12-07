import json

from ..models import TimeEntry
from .output import OutputFormatter


class JsonOutput(OutputFormatter):
    def single_entry_output(self, entry: TimeEntry | None) -> None:
        if entry is None:
            print("No active time record.")
            return
        print(json.dumps(entry.model_dump(mode="json")))

    def multiple_entries_output(self, entries: list[TimeEntry]) -> None:
        print(json.dumps([entry.model_dump(mode="json") for entry in entries]))
