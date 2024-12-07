import sys
from typing import Self

from ..models import TimeEntry


class OutputFormatter:
    """The Base OutputFormatter class that all output classes should inherit from."""

    def __init__(self):
        pass

    def single_entry_output(self, entry: TimeEntry) -> None:
        raise NotImplementedError("output method is not implemented")

    def multiple_entries_output(self, entries: list[TimeEntry]) -> None:
        raise NotImplementedError("output method is not implemented")

    @classmethod
    def create(cls, output_format: str, force: bool = False) -> Self:
        """Factory method to create the correct output class based on the output format."""
        if not force:
            if sys.stdout.isatty() and output_format in ("", "rich"):
                output_format = "rich"
            elif (not sys.stdout.isatty() and output_format == "") or output_format == "json":
                output_format = "json"
            else:
                output_format = "text"
        if output_format == "text":
            from .text_output import RawTextOutput

            return RawTextOutput()
        if output_format == "json":
            from .json_output import JsonOutput

            return JsonOutput()
        if output_format == "rich":
            from .rich_text_output import RichTextOutput

            return RichTextOutput()
        raise ValueError(f"Unsupported output format: {output_format}")
