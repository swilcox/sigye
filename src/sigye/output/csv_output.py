import csv
import sys
from typing import Any

from ..models import TimeEntry
from .output import OutputFormatter


class CsvOutput(OutputFormatter):
    def _get_header(self):
        return [
            "id",
            "start_time",
            "end_time",
            "project",
            "comment",
            "tags",
        ]

    def _get_row(self, entry: TimeEntry):
        return [
            entry.id,
            entry.naive_start_time.strftime("%Y-%m-%d %H:%M:%S"),
            entry.naive_end_time.strftime("%Y-%m-%d %H:%M:%S") if entry.naive_end_time else "",
            entry.project,
            entry.comment,
            "|".join(entry.tags),
        ]

    def _send_output(self, output: list[list[Any]]) -> None:
        writer = csv.writer(sys.stdout)
        writer.writerows(output)

    def single_entry_output(self, entry: TimeEntry | None) -> None:
        if entry is None:
            return
        self._send_output([self._get_header(), self._get_row(entry)])

    def multiple_entries_output(self, entries: list[TimeEntry]) -> None:
        self._send_output([self._get_header()] + [self._get_row(entry) for entry in entries])

    def export_output(self, count: int, filename: str) -> None:
        self._send_output([["exported", "filename"], [count, filename]])
