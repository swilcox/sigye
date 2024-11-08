from datetime import date
from rich.console import Console
from rich.table import Table
from ..models import TimeEntry


def single_entry_output(entry: TimeEntry):
    table = Table(title="Time Entry")
    table.add_column("field")
    table.add_column("value")
    table.add_row("ID", entry.id)
    table.add_row("start date/time", f"{entry.naive_start_time:%Y-%m-%d %H:%M:%S}")
    table.add_row(
        "end time", f"{entry.naive_end_time:%H:%M:%S}" if entry.end_time else "-"
    )
    table.add_row("duration", entry.humanized_duration)
    table.add_row("project", entry.project)
    table.add_row("comments", entry.comment)
    table.add_row("tags", ", ".join(tag for tag in entry.tags))
    console = Console()
    console.print(table)


def list_output(entry_list: list[TimeEntry]):
    table = Table(title="Time Entries")
    table.add_column("start", justify="right", style="cyan")
    table.add_column("end", justify="right", style="magenta")
    table.add_column("delta", style="cyan")
    table.add_column("project", justify="left", style="green")
    table.add_column("comments", style="blue")
    table.add_column("tags", style="red")
    current_date = date(1970, 1, 1)
    for entry in entry_list:
        if entry.start_time.date() != current_date:
            current_date = entry.start_time.date()
            table.add_section()
            table.add_row(f"{current_date:%Y-%m-%d}", style="yellow")
        table.add_row(
            f"{entry.naive_start_time:%H:%M:%S}",
            f"{entry.naive_end_time:%H:%M:%S}" if entry.end_time else "-",
            f"{entry.humanized_duration}",
            entry.project,
            entry.comment,
            ", ".join(tag for tag in entry.tags),
        )
    console = Console()
    console.print(table)
