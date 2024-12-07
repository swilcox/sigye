from ..models import TimeEntry
from .output import OutputFormatter


class RawTextOutput(OutputFormatter):
    def _entry_to_str(self, entry: TimeEntry) -> str:
        return f"{entry.id} {entry.start_time} {entry.end_time} {entry.project} {entry.comment} {entry.tags}"

    def single_entry_output(self, entry: TimeEntry | None) -> None:
        if entry is None:
            print("No active time record.")
            return
        print(self._entry_to_str(entry))

    def multiple_entries_output(self, entries: list[TimeEntry]) -> None:
        for entry in entries:
            print(self._entry_to_str(entry))
