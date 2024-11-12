from datetime import date
from rich.console import Console
from rich.table import Table
from ..models import TimeEntry
from ..utils.translation import gettext as _


ABBR_ID_LENGTH = 4


def single_entry_output(entry: TimeEntry):
    table = Table(title=_("Time Record"))
    table.add_column(_("field"))
    table.add_column(_("value"))
    table.add_row(
        _("ID"),
        f"[magenta]{entry.id[0:ABBR_ID_LENGTH]}[/magenta]{entry.id[ABBR_ID_LENGTH:]}",
    )
    table.add_row(
        _("start time"), f"[cyan]{entry.naive_start_time:%Y-%m-%d %H:%M:%S}[/cyan]"
    )
    table.add_row(
        _("end time"),
        f"[magenta]{entry.naive_end_time:%H:%M:%S}[/magenta]"
        if entry.end_time
        else "-",
    )
    table.add_row(_("delta"), f"[cyan]{entry.humanized_duration}[/cyan]")
    table.add_row(_("project"), f"[green]{entry.project}[/green]")
    table.add_row(_("comments"), f"[blue]{entry.comment}[/blue]")
    table.add_row(_("tags"), "[red]" + ", ".join(tag for tag in entry.tags) + "[/red]")
    console = Console()
    console.print(table)


def list_output(entry_list: list[TimeEntry]):
    table = Table(title=_("Time Records"))
    table.add_column(_("id"), justify="left", style="#707070")
    table.add_column(_("start"), justify="right", style="cyan")
    table.add_column(_("end"), justify="right", style="magenta")
    table.add_column(_("delta"), style="cyan")
    table.add_column(_("project"), justify="left", style="green")
    table.add_column(_("comments"), style="blue")
    table.add_column(_("tags"), style="red")
    current_date = date(1970, 1, 1)
    for entry in entry_list:
        if entry.start_time.date() != current_date:
            current_date = entry.start_time.date()
            table.add_section()
            table.add_row("", f"{current_date:%Y-%m-%d}", style="yellow")
        table.add_row(
            f"{entry.id[0:ABBR_ID_LENGTH]}",
            f"{entry.naive_start_time:%H:%M:%S}",
            f"{entry.naive_end_time:%H:%M:%S}" if entry.end_time else "-",
            f"{entry.humanized_duration}",
            entry.project,
            entry.comment,
            ", ".join(tag for tag in entry.tags),
        )
    console = Console()
    console.print(table)
