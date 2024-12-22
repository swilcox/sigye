from datetime import timedelta
from pathlib import Path

from jinja2 import Template
from pydantic import BaseModel

from ..models import TimeEntry
from ..utils.datetime_utils import format_delta
from .output import OutputFormatter

SINGLE_ENTRY = Template(
    """
# Time Entry

| field | value |
|-------|-------|
| ID | {{ entry.id }} |
| Start Time | {{ entry.naive_start_time.strftime("%Y-%m-%d %H:%M:%S") }} |
| Stop Time | {{ entry.naive_end_time.strftime("%Y-%m-%d %H:%M:%S") }} |
| Delta | {{ entry.humanized_duration }} |
| Project | {{ entry.project }} |
| Comment | {{ entry.comment }} |
| Tags | {{ entry.tags }} |
"""
)


MULTIPLE_ENTRIES = Template(
    """
# Time Entries

| ID | Start Time| Stop Time| Delta |Project |Comment |Tags |
|----|----------:|---------:|------:|--------|--------|-----|
{% for entry in entries %}{% if 'total_duration' in entry.model_fields_set %}| | {{ entry.total_description }}| | {{ entry.total_duration }} | | | |{% else %}| {{ entry.id[0:4] }} | {{ entry.naive_start_time.strftime("%Y-%m-%d %H:%M:%S") }}| {{ entry.naive_end_time.strftime("%H:%M:%S") }} | {{ entry.humanized_duration }}| {{ entry.project }} | {{ entry.comment }} | {{ ", ".join(entry.tags) }} |{% endif %}
{% endfor %}
"""  # noqa: E501
)


EXPORT_OUTPUT = Template(
    """
Exported {{ count }} entries to {{ filename }}
"""
)


class OutputModel(BaseModel):
    total_description: str = ""
    total_duration: str = ""


class MarkdownOutput(OutputFormatter):
    def single_entry_output(self, entry: TimeEntry | None) -> None:
        if entry is None:
            print("No active time record.")
        else:
            print(SINGLE_ENTRY.render(entry=entry))

    def multiple_entries_output(self, entries: list[TimeEntry]) -> None:
        output_entries = []
        if len(entries):
            current_date = entries[0].naive_start_time.date()
            subtotal_delta = timedelta(0)
            total_delta = timedelta(0)
            for entry in entries:
                total_delta += (entry.naive_end_time - entry.naive_start_time) if entry.naive_end_time else timedelta(0)
                if entry.naive_start_time.date() != current_date:
                    output_entries.append(
                        OutputModel(total_description="*subtotal*", total_duration=format_delta(subtotal_delta))
                    )
                    current_date = entry.naive_start_time.date()
                    subtotal_delta = timedelta(0)
                subtotal_delta += (
                    (entry.naive_end_time - entry.naive_start_time) if entry.naive_end_time else timedelta(0)
                )
                output_entries.append(entry)
            output_entries.append(
                OutputModel(total_description="*subtotal*", total_duration=format_delta(subtotal_delta))
            )
            output_entries.append(OutputModel(total_description="**total**", total_duration=format_delta(total_delta)))
        print(MULTIPLE_ENTRIES.render(entries=output_entries))

    def export_output(self, count: int, filename: Path | str) -> None:
        print(EXPORT_OUTPUT.render(count=count, filename=filename))
